"""
Bot Configuration Manager
Loads and manages multiple bot configurations from JSON and YAML files

v0.4.1 Enhancement:
- Support for YAML configuration files (prompts/configs/*.yaml)
- Backwards compatible with existing JSON files (bots/*.json)
- File-based prompt integration (bot personality in separate .md files)
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any, List

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("[BotManager] ⚠️  PyYAML not installed - YAML configs not available")


class BotConfig:
    """Represents a single bot configuration"""

    def __init__(self, config_data: Dict[str, Any]):
        """
        Initialize bot configuration from dictionary

        Args:
            config_data: Dictionary containing bot configuration
        """
        import os

        self.bot_id = config_data.get('bot_id', 'default')

        # Check for environment variable override first (for local testing)
        env_var_name = f"BOT_KEY_{self.bot_id.upper()}"
        self.bot_key = os.getenv(env_var_name, config_data.get('bot_key'))
        self.name = config_data.get('name', 'AI Assistant')
        self.display_name = config_data.get('display_name', self.name)
        self.description = config_data.get('description', '')

        # Model configuration
        model_config = config_data.get('model_config', {})
        self.model = model_config.get('model', 'claude-3-5-haiku-20241022')
        self.temperature = model_config.get('temperature', 1.0)
        self.max_tokens = model_config.get('max_tokens', 4096)

        thinking_config = model_config.get('thinking', {})
        self.thinking_enabled = thinking_config.get('enabled', False)
        self.thinking_budget = thinking_config.get('budget_tokens', 0)

        # System prompt
        self.system_prompt = config_data.get('system_prompt', '')

        # v0.4.1: File-based prompts support
        self.system_prompt_file = config_data.get('system_prompt_file')

        # Tools and capabilities
        # v0.4.0: New structure with mcp_servers and tools dict
        self.mcp_servers = config_data.get('mcp_servers', ['campfire'])  # Default to campfire MCP
        self.tools = config_data.get('tools', {})  # Dict: {builtin: [...], campfire: [...], skills: [...]}

        # Backwards compatibility: if old tools_enabled exists, convert it
        self.tools_enabled = config_data.get('tools_enabled', [])
        if self.tools_enabled and not self.tools:
            # Legacy format - all tools assumed to be in campfire MCP
            self.tools = {'campfire': self.tools_enabled}

        self.capabilities = config_data.get('capabilities', {})

        # Language settings
        self.languages = config_data.get('languages', ['en'])
        self.default_language = config_data.get('default_language', 'en')

        # Other settings
        self.settings = config_data.get('settings', {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert bot config to dictionary"""
        return {
            'bot_id': self.bot_id,
            'bot_key': self.bot_key,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'thinking_enabled': self.thinking_enabled,
            'thinking_budget': self.thinking_budget,
            'system_prompt': self.system_prompt,
            'system_prompt_file': self.system_prompt_file,  # v0.4.1: File-based prompts
            'mcp_servers': self.mcp_servers,
            'tools': self.tools,
            'tools_enabled': self.tools_enabled,  # Legacy, kept for compatibility
            'capabilities': self.capabilities,
            'languages': self.languages,
            'default_language': self.default_language,
            'settings': self.settings
        }


class BotManager:
    """Manages multiple bot configurations"""

    def __init__(self, bots_dirs: List[str] = None):
        """
        Initialize BotManager

        Args:
            bots_dirs: List of directories to search for bot configs
                      Default: ['./bots', 'prompts/configs']
                      Supports both JSON and YAML files
        """
        if bots_dirs is None:
            bots_dirs = ['./bots', 'prompts/configs']

        self.bots_dirs = [Path(d) for d in bots_dirs]
        self.bots: Dict[str, BotConfig] = {}
        self.bots_by_key: Dict[str, BotConfig] = {}
        self.default_bot: Optional[BotConfig] = None

        self._load_all_bots()

    def _load_all_bots(self):
        """
        Load all bot configurations from JSON and YAML files.

        Searches multiple directories:
        - ./bots/*.json (legacy JSON configs)
        - prompts/configs/*.yaml (new YAML configs)

        YAML files take precedence over JSON if both exist for same bot_id.
        """
        config_files = []

        # Collect all config files from all directories
        for bots_dir in self.bots_dirs:
            if not bots_dir.exists():
                print(f"[BotManager] ⚠️  Config directory not found: {bots_dir}")
                continue

            # Find JSON files
            json_files = list(bots_dir.glob('*.json'))
            config_files.extend([(f, 'json') for f in json_files])

            # Find YAML files (if PyYAML available)
            if YAML_AVAILABLE:
                yaml_files = list(bots_dir.glob('*.yaml'))
                yaml_files.extend(bots_dir.glob('*.yml'))
                config_files.extend([(f, 'yaml') for f in yaml_files])

        if not config_files:
            print("[BotManager] ⚠️  No bot configurations found in any directory")
            print("[BotManager] Loading default bot only")
            self._load_default_bot()
            return

        # Load each config file
        for config_file, file_type in config_files:
            try:
                config_data = self._load_config_file(config_file, file_type)

                if not config_data:
                    continue

                bot_config = BotConfig(config_data)

                # YAML files override JSON for same bot_id
                if bot_config.bot_id in self.bots and file_type == 'yaml':
                    print(f"[BotManager] 🔄 YAML config overrides JSON for: {bot_config.bot_id}")

                self.bots[bot_config.bot_id] = bot_config

                # Index by bot_key if available
                if bot_config.bot_key:
                    self.bots_by_key[bot_config.bot_key] = bot_config

                # Set default bot
                if bot_config.bot_id == 'default':
                    self.default_bot = bot_config

                file_type_label = file_type.upper()
                print(f"[BotManager] ✅ Loaded {file_type_label}: {bot_config.display_name} ({bot_config.bot_id})")

            except Exception as e:
                print(f"[BotManager] ❌ Error loading config from {config_file}: {e}")

        # Ensure we have a default bot
        if not self.default_bot and self.bots:
            # Use first bot as default
            self.default_bot = list(self.bots.values())[0]
            print(f"[BotManager] Using {self.default_bot.display_name} as default bot")

    def _load_config_file(self, config_file: Path, file_type: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from JSON or YAML file.

        Args:
            config_file: Path to config file
            file_type: 'json' or 'yaml'

        Returns:
            Configuration dictionary or None if loading fails
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if file_type == 'json':
                    return json.load(f)
                elif file_type == 'yaml' and YAML_AVAILABLE:
                    return yaml.safe_load(f)
                else:
                    return None

        except Exception as e:
            print(f"[BotManager] ❌ Error reading {file_type} file {config_file}: {e}")
            return None

    def _load_default_bot(self):
        """Load a minimal default bot configuration"""
        default_config = {
            'bot_id': 'default',
            'bot_key': None,
            'name': 'AI Assistant',
            'system_prompt': 'You are a helpful AI assistant.',
            'model_config': {
                'model': 'claude-3-5-haiku-20241022',
                'temperature': 1.0,
                'max_tokens': 4096
            }
        }
        self.default_bot = BotConfig(default_config)
        self.bots['default'] = self.default_bot
        print("Loaded minimal default bot configuration")

    def get_bot_by_id(self, bot_id: str) -> Optional[BotConfig]:
        """
        Get bot configuration by bot_id

        Args:
            bot_id: Bot identifier

        Returns:
            BotConfig if found, None otherwise
        """
        return self.bots.get(bot_id)

    def get_bot_by_key(self, bot_key: str) -> Optional[BotConfig]:
        """
        Get bot configuration by bot_key

        Args:
            bot_key: Bot authentication key (e.g., "2-CsheovnLtzjM")

        Returns:
            BotConfig if found, None otherwise
        """
        return self.bots_by_key.get(bot_key)

    def get_default_bot(self) -> BotConfig:
        """
        Get default bot configuration

        Returns:
            Default BotConfig
        """
        if not self.default_bot:
            self._load_default_bot()
        return self.default_bot

    def list_bots(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available bots

        Returns:
            Dictionary of bot_id -> bot info
        """
        return {
            bot_id: {
                'name': bot.name,
                'display_name': bot.display_name,
                'description': bot.description,
                'bot_key': bot.bot_key,
                'model': bot.model
            }
            for bot_id, bot in self.bots.items()
        }

    def load_bot_config(self, bot_id: str) -> Optional[BotConfig]:
        """
        Load a single bot configuration on-demand.

        Searches all configured directories for bot config file.
        Useful for loading bot configs dynamically.

        Args:
            bot_id: Bot identifier

        Returns:
            BotConfig if found, None otherwise
        """
        # Check if already loaded
        if bot_id in self.bots:
            return self.bots[bot_id]

        # Search for config file
        for bots_dir in self.bots_dirs:
            if not bots_dir.exists():
                continue

            # Try YAML first (if available)
            if YAML_AVAILABLE:
                yaml_file = bots_dir / f"{bot_id}.yaml"
                if yaml_file.exists():
                    config_data = self._load_config_file(yaml_file, 'yaml')
                    if config_data:
                        bot_config = BotConfig(config_data)
                        self.bots[bot_id] = bot_config
                        return bot_config

            # Try JSON
            json_file = bots_dir / f"{bot_id}.json"
            if json_file.exists():
                config_data = self._load_config_file(json_file, 'json')
                if config_data:
                    bot_config = BotConfig(config_data)
                    self.bots[bot_id] = bot_config
                    return bot_config

        return None

    def reload_bots(self):
        """Reload all bot configurations from disk"""
        self.bots.clear()
        self.bots_by_key.clear()
        self.default_bot = None
        self._load_all_bots()
        print("[BotManager] Bot configurations reloaded")
