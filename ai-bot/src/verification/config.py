"""
Per-Bot Verification Configuration

Allows each bot to configure verification behavior independently:
- Mode: lenient (warn), strict (block), or off (disabled)
- Rules: Specific validation rules to enable
- Logging: Whether to log warnings/errors
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class VerificationMode(str, Enum):
    """Verification strictness levels"""
    LENIENT = "lenient"  # Warn but allow (default)
    STRICT = "strict"    # Block invalid requests
    OFF = "off"          # Disabled (no verification)


@dataclass
class VerificationConfig:
    """Per-bot verification configuration"""

    mode: VerificationMode = VerificationMode.LENIENT
    log_warnings: bool = True
    log_errors: bool = True

    # Enabled validation rules
    rules: List[str] = None

    def __post_init__(self):
        """Set default rules if not provided"""
        if self.rules is None:
            # Default rules for lenient mode
            self.rules = [
                "validate_dates",
                "validate_positive_numbers",
                "validate_percentages",
                "validate_required_fields",
            ]

    @classmethod
    def from_dict(cls, config: Dict) -> 'VerificationConfig':
        """Load configuration from dictionary"""
        mode_str = config.get('mode', 'lenient')
        mode = VerificationMode(mode_str)

        return cls(
            mode=mode,
            log_warnings=config.get('log_warnings', True),
            log_errors=config.get('log_errors', True),
            rules=config.get('rules', None),
        )

    def is_enabled(self) -> bool:
        """Check if verification is enabled"""
        return self.mode != VerificationMode.OFF

    def should_block(self) -> bool:
        """Check if verification should block invalid requests"""
        return self.mode == VerificationMode.STRICT

    def should_warn(self) -> bool:
        """Check if verification should warn on invalid requests"""
        return self.mode == VerificationMode.LENIENT


# Default configurations per bot
BOT_CONFIGS: Dict[str, VerificationConfig] = {
    "personal_assistant": VerificationConfig(
        mode=VerificationMode.LENIENT,
        log_warnings=True,
        rules=[
            "validate_dates",
            "validate_positive_numbers",
            "validate_required_fields",
        ],
    ),

    "financial_analyst": VerificationConfig(
        mode=VerificationMode.STRICT,  # Financial calculations require strictness
        log_warnings=True,
        log_errors=True,
        rules=[
            "validate_dates",
            "validate_positive_numbers",
            "validate_percentages",
            "validate_financial_balance",
            "validate_required_fields",
        ],
    ),

    "operations_assistant": VerificationConfig(
        mode=VerificationMode.LENIENT,
        log_warnings=True,
        rules=[
            "validate_dates",
            "validate_positive_numbers",
            "validate_percentages",
            "validate_required_fields",
        ],
    ),

    "menu_engineer": VerificationConfig(
        mode=VerificationMode.LENIENT,
        log_warnings=True,
        rules=[
            "validate_positive_numbers",
            "validate_percentages",
            "validate_required_fields",
        ],
    ),

    # Default for all other bots
    "default": VerificationConfig(
        mode=VerificationMode.LENIENT,
        log_warnings=True,
        rules=[
            "validate_dates",
            "validate_positive_numbers",
            "validate_required_fields",
        ],
    ),
}


def get_verification_config(bot_id: str) -> VerificationConfig:
    """
    Get verification configuration for a specific bot.

    Args:
        bot_id: Bot identifier (e.g., "personal_assistant")

    Returns:
        VerificationConfig for the bot, or default config if not found
    """
    return BOT_CONFIGS.get(bot_id, BOT_CONFIGS["default"])


def is_verification_enabled(bot_id: str) -> bool:
    """Check if verification is enabled for a bot"""
    config = get_verification_config(bot_id)
    return config.is_enabled()


def should_block_on_error(bot_id: str) -> bool:
    """Check if bot should block on verification errors"""
    config = get_verification_config(bot_id)
    return config.should_block()
