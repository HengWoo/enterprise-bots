"""
Tests for verification configuration

Coverage: Configuration loading, per-bot settings, mode validation
"""

import pytest
from src.verification.config import (
    VerificationConfig,
    VerificationMode,
    get_verification_config,
    is_verification_enabled,
    should_block_on_error,
    BOT_CONFIGS,
)


class TestVerificationMode:
    """Test VerificationMode enum"""

    def test_mode_values(self):
        """Test mode enum values"""
        assert VerificationMode.LENIENT == "lenient"
        assert VerificationMode.STRICT == "strict"
        assert VerificationMode.OFF == "off"

    def test_mode_from_string(self):
        """Test creating mode from string"""
        assert VerificationMode("lenient") == VerificationMode.LENIENT
        assert VerificationMode("strict") == VerificationMode.STRICT
        assert VerificationMode("off") == VerificationMode.OFF


class TestVerificationConfig:
    """Test VerificationConfig dataclass"""

    def test_default_config(self):
        """Test default configuration"""
        config = VerificationConfig()
        assert config.mode == VerificationMode.LENIENT
        assert config.log_warnings is True
        assert config.log_errors is True
        assert config.rules is not None
        assert len(config.rules) == 4

    def test_custom_config(self):
        """Test custom configuration"""
        config = VerificationConfig(
            mode=VerificationMode.STRICT,
            log_warnings=False,
            rules=["validate_dates"],
        )
        assert config.mode == VerificationMode.STRICT
        assert config.log_warnings is False
        assert config.rules == ["validate_dates"]

    def test_from_dict_lenient(self):
        """Test loading from dict - lenient mode"""
        config_dict = {
            "mode": "lenient",
            "log_warnings": True,
            "rules": ["validate_dates", "validate_positive_numbers"],
        }
        config = VerificationConfig.from_dict(config_dict)
        assert config.mode == VerificationMode.LENIENT
        assert config.log_warnings is True
        assert len(config.rules) == 2

    def test_from_dict_strict(self):
        """Test loading from dict - strict mode"""
        config_dict = {
            "mode": "strict",
            "log_errors": True,
        }
        config = VerificationConfig.from_dict(config_dict)
        assert config.mode == VerificationMode.STRICT
        assert config.log_errors is True

    def test_from_dict_defaults(self):
        """Test loading from dict with defaults"""
        config = VerificationConfig.from_dict({})
        assert config.mode == VerificationMode.LENIENT
        assert config.log_warnings is True

    def test_is_enabled(self):
        """Test is_enabled check"""
        config_on = VerificationConfig(mode=VerificationMode.LENIENT)
        assert config_on.is_enabled() is True

        config_off = VerificationConfig(mode=VerificationMode.OFF)
        assert config_off.is_enabled() is False

    def test_should_block(self):
        """Test should_block check"""
        config_strict = VerificationConfig(mode=VerificationMode.STRICT)
        assert config_strict.should_block() is True

        config_lenient = VerificationConfig(mode=VerificationMode.LENIENT)
        assert config_lenient.should_block() is False

    def test_should_warn(self):
        """Test should_warn check"""
        config_lenient = VerificationConfig(mode=VerificationMode.LENIENT)
        assert config_lenient.should_warn() is True

        config_strict = VerificationConfig(mode=VerificationMode.STRICT)
        assert config_strict.should_warn() is False


class TestBotConfigurations:
    """Test bot-specific configurations"""

    def test_personal_assistant_config(self):
        """Test personal_assistant configuration"""
        config = BOT_CONFIGS["personal_assistant"]
        assert config.mode == VerificationMode.LENIENT
        assert config.log_warnings is True
        assert "validate_dates" in config.rules

    def test_financial_analyst_config(self):
        """Test financial_analyst configuration (strict mode)"""
        config = BOT_CONFIGS["financial_analyst"]
        assert config.mode == VerificationMode.STRICT
        assert config.log_errors is True
        assert "validate_financial_balance" in config.rules

    def test_operations_assistant_config(self):
        """Test operations_assistant configuration"""
        config = BOT_CONFIGS["operations_assistant"]
        assert config.mode == VerificationMode.LENIENT
        assert "validate_percentages" in config.rules

    def test_menu_engineer_config(self):
        """Test menu_engineer configuration"""
        config = BOT_CONFIGS["menu_engineer"]
        assert config.mode == VerificationMode.LENIENT
        assert "validate_positive_numbers" in config.rules

    def test_default_config(self):
        """Test default configuration"""
        config = BOT_CONFIGS["default"]
        assert config.mode == VerificationMode.LENIENT
        assert len(config.rules) > 0


class TestConfigurationHelpers:
    """Test configuration helper functions"""

    def test_get_verification_config_known_bot(self):
        """Test getting config for known bot"""
        config = get_verification_config("personal_assistant")
        assert config is not None
        assert config.mode == VerificationMode.LENIENT

    def test_get_verification_config_unknown_bot(self):
        """Test getting config for unknown bot (returns default)"""
        config = get_verification_config("unknown_bot")
        assert config is not None
        assert config == BOT_CONFIGS["default"]

    def test_is_verification_enabled_true(self):
        """Test verification enabled check - true case"""
        assert is_verification_enabled("personal_assistant") is True
        assert is_verification_enabled("financial_analyst") is True

    def test_is_verification_enabled_default(self):
        """Test verification enabled for unknown bot"""
        # Unknown bots get default config (lenient mode)
        assert is_verification_enabled("unknown_bot") is True

    def test_should_block_on_error_financial(self):
        """Test blocking behavior for financial_analyst"""
        # Financial analyst is in strict mode
        assert should_block_on_error("financial_analyst") is True

    def test_should_block_on_error_personal(self):
        """Test blocking behavior for personal_assistant"""
        # Personal assistant is in lenient mode
        assert should_block_on_error("personal_assistant") is False

    def test_should_block_on_error_unknown(self):
        """Test blocking behavior for unknown bot"""
        # Unknown bots get default config (lenient mode)
        assert should_block_on_error("unknown_bot") is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
