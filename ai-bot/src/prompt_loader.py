"""
PromptLoader - File-based prompt management following Anthropic Cookbook patterns

This module implements a simple, file-based prompt loading system that follows
Anthropic's best practices:
- Prompts stored in .md files
- Simple string.Template variable substitution (NOT Jinja2)
- Separation of bot personality from domain expertise (Skills)
- YAML for bot metadata, Markdown for prompt content

Architecture:
- Layer 1: Bot Personality (prompts/bots/*.md) - Always loaded
- Layer 2: Skills (prompts/skills/*/SKILL.md) - Loaded on-demand
- Layer 3: Dynamic Context (runtime injection) - Date, user, room, files

Example file structure:
    prompts/
    ├── bots/
    │   ├── personal_assistant.md
    │   └── financial_analyst.md
    ├── skills/
    │   ├── document-skills-docx/
    │   │   ├── SKILL.md
    │   │   └── resources/
    │   └── presentation-generation/
    │       ├── SKILL.md
    │       └── resources/
    ├── shared/
    │   ├── security_rules.md
    │   └── html_formatting.md
    └── configs/
        └── personal_assistant.yaml

Usage:
    loader = PromptLoader(prompts_dir="prompts")

    # Load bot personality
    context = {
        "current_date": "2025-10-29",
        "user_name": "John",
        "room_name": "Project Alpha"
    }
    prompt = loader.load_bot_prompt("personal_assistant", context)

    # Load shared section
    security = loader.load_shared_section("security_rules")

    # Check if bot has file-based prompt
    has_prompt = loader.has_file_based_prompt("personal_assistant")
"""

from string import Template
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Simple file-based prompt loader following Anthropic Cookbook pattern.

    Uses Python's string.Template for simple $variable substitution:
    - No conditionals or loops (unlike Jinja2)
    - Safe and predictable
    - Matches Anthropic's approach exactly
    """

    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize PromptLoader.

        Args:
            prompts_dir: Root directory for prompts (default: "prompts")
        """
        self.prompts_dir = Path(prompts_dir)

        # Validate directory structure
        self._validate_structure()

        logger.info(f"[PromptLoader] Initialized with prompts_dir: {self.prompts_dir}")

    def _validate_structure(self):
        """Validate that required directories exist."""
        required_dirs = ["bots", "skills", "shared", "configs"]

        for dir_name in required_dirs:
            dir_path = self.prompts_dir / dir_name
            if not dir_path.exists():
                logger.warning(f"[PromptLoader] ⚠️  Missing directory: {dir_path}")

    def has_file_based_prompt(self, bot_id: str) -> bool:
        """
        Check if bot has a file-based prompt.

        Args:
            bot_id: Bot identifier (e.g., "personal_assistant")

        Returns:
            True if prompts/bots/{bot_id}.md exists
        """
        prompt_file = self.prompts_dir / "bots" / f"{bot_id}.md"
        return prompt_file.exists()

    def load_bot_prompt(self, bot_id: str, context: Dict[str, str]) -> str:
        """
        Load bot personality prompt from .md file and substitute variables.

        This follows Anthropic Cookbook pattern:
        - Simple $variable substitution using string.Template
        - No complex logic or conditionals
        - Predictable and safe

        Args:
            bot_id: Bot identifier (e.g., "personal_assistant")
            context: Dictionary of variables to substitute (e.g., {"current_date": "2025-10-29"})

        Returns:
            Processed prompt string with variables substituted

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            KeyError: If template variable missing from context

        Example:
            context = {
                "current_date": "2025-10-29",
                "user_name": "John",
                "room_name": "Project Alpha"
            }
            prompt = loader.load_bot_prompt("personal_assistant", context)
        """
        prompt_file = self.prompts_dir / "bots" / f"{bot_id}.md"

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        # Load raw prompt content
        prompt_content = prompt_file.read_text(encoding='utf-8')

        # Simple variable substitution (Anthropic pattern)
        template = Template(prompt_content)

        try:
            processed_prompt = template.substitute(**context)
            logger.info(f"[PromptLoader] ✅ Loaded prompt for bot: {bot_id}")
            return processed_prompt
        except KeyError as e:
            logger.error(f"[PromptLoader] ❌ Missing template variable: {e}")
            # Use safe_substitute as fallback (leaves missing variables as-is)
            processed_prompt = template.safe_substitute(**context)
            logger.warning(f"[PromptLoader] ⚠️  Used safe_substitute (some variables missing)")
            return processed_prompt

    def load_shared_section(self, section_name: str) -> str:
        """
        Load reusable prompt section from shared/ directory.

        Shared sections are text fragments that can be included in multiple bots:
        - security_rules.md
        - html_formatting.md
        - work_principles.md

        Args:
            section_name: Name of shared section (without .md extension)

        Returns:
            Content of shared section

        Raises:
            FileNotFoundError: If section file doesn't exist

        Example:
            security = loader.load_shared_section("security_rules")
        """
        section_file = self.prompts_dir / "shared" / f"{section_name}.md"

        if not section_file.exists():
            raise FileNotFoundError(f"Shared section not found: {section_file}")

        content = section_file.read_text(encoding='utf-8')
        logger.info(f"[PromptLoader] ✅ Loaded shared section: {section_name}")
        return content

    def list_available_prompts(self) -> List[str]:
        """
        List all available file-based prompts.

        Returns:
            List of bot IDs that have .md prompt files

        Example:
            available = loader.list_available_prompts()
            # Returns: ["personal_assistant", "financial_analyst", ...]
        """
        bots_dir = self.prompts_dir / "bots"

        if not bots_dir.exists():
            return []

        prompt_files = bots_dir.glob("*.md")
        bot_ids = [f.stem for f in prompt_files]

        logger.info(f"[PromptLoader] Found {len(bot_ids)} file-based prompts: {bot_ids}")
        return bot_ids

    def list_shared_sections(self) -> List[str]:
        """
        List all available shared sections.

        Returns:
            List of shared section names

        Example:
            sections = loader.list_shared_sections()
            # Returns: ["security_rules", "html_formatting", ...]
        """
        shared_dir = self.prompts_dir / "shared"

        if not shared_dir.exists():
            return []

        section_files = shared_dir.glob("*.md")
        section_names = [f.stem for f in section_files]

        logger.info(f"[PromptLoader] Found {len(section_names)} shared sections: {section_names}")
        return section_names

    def get_prompt_file_path(self, bot_id: str) -> Path:
        """
        Get full path to bot's prompt file.

        Args:
            bot_id: Bot identifier

        Returns:
            Path object to prompt file

        Example:
            path = loader.get_prompt_file_path("personal_assistant")
            # Returns: Path("prompts/bots/personal_assistant.md")
        """
        return self.prompts_dir / "bots" / f"{bot_id}.md"

    def load_raw_prompt(self, bot_id: str) -> str:
        """
        Load raw prompt content without variable substitution.

        Useful for testing, debugging, or template analysis.

        Args:
            bot_id: Bot identifier

        Returns:
            Raw prompt content with $variables intact

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = self.get_prompt_file_path(bot_id)

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        return prompt_file.read_text(encoding='utf-8')


# Convenience function for quick prompt loading
def load_prompt(bot_id: str, context: Dict[str, str], prompts_dir: str = "prompts") -> str:
    """
    Convenience function to load prompt in one line.

    Args:
        bot_id: Bot identifier
        context: Template variables
        prompts_dir: Root prompts directory (default: "prompts")

    Returns:
        Processed prompt string

    Example:
        prompt = load_prompt("personal_assistant", {"current_date": "2025-10-29"})
    """
    loader = PromptLoader(prompts_dir)
    return loader.load_bot_prompt(bot_id, context)
