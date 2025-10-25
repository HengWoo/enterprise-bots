"""
Bot Configuration Manager
Loads and manages multiple bot configurations from JSON files
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


class BotConfig:
    """Represents a single bot configuration"""

    def __init__(self, config_data: Dict[str, Any]):
        """
        Initialize bot configuration from dictionary

        Args:
            config_data: Dictionary containing bot configuration
        """
        self.bot_id = config_data.get('bot_id', 'default')
        self.bot_key = config_data.get('bot_key')
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

        # Tools and capabilities
        self.tools_enabled = config_data.get('tools_enabled', [])
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
            'tools_enabled': self.tools_enabled,
            'capabilities': self.capabilities,
            'languages': self.languages,
            'default_language': self.default_language,
            'settings': self.settings
        }


class BotManager:
    """Manages multiple bot configurations"""

    def __init__(self, bots_dir: str = './bots'):
        """
        Initialize BotManager

        Args:
            bots_dir: Directory containing bot configuration JSON files
        """
        self.bots_dir = Path(bots_dir)
        self.bots: Dict[str, BotConfig] = {}
        self.bots_by_key: Dict[str, BotConfig] = {}
        self.default_bot: Optional[BotConfig] = None

        self._load_all_bots()

    def _load_all_bots(self):
        """Load all bot configurations from JSON files"""
        if not self.bots_dir.exists():
            print(f"Warning: Bots directory not found: {self.bots_dir}")
            print("Creating directory and loading default bot only")
            self.bots_dir.mkdir(parents=True, exist_ok=True)
            self._load_default_bot()
            return

        # Load all JSON files in bots directory
        json_files = list(self.bots_dir.glob('*.json'))

        if not json_files:
            print(f"Warning: No bot configurations found in {self.bots_dir}")
            self._load_default_bot()
            return

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                bot_config = BotConfig(config_data)
                self.bots[bot_config.bot_id] = bot_config

                # Index by bot_key if available
                if bot_config.bot_key:
                    self.bots_by_key[bot_config.bot_key] = bot_config

                # Set default bot
                if bot_config.bot_id == 'default':
                    self.default_bot = bot_config

                print(f"Loaded bot: {bot_config.display_name} ({bot_config.bot_id})")

            except Exception as e:
                print(f"Error loading bot config from {json_file}: {e}")

        # Ensure we have a default bot
        if not self.default_bot and self.bots:
            # Use first bot as default
            self.default_bot = list(self.bots.values())[0]
            print(f"Using {self.default_bot.display_name} as default bot")

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

    def reload_bots(self):
        """Reload all bot configurations from disk"""
        self.bots.clear()
        self.bots_by_key.clear()
        self.default_bot = None
        self._load_all_bots()
        print("Bot configurations reloaded")
