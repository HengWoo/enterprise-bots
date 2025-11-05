"""
Verification System for Campfire AI Bots

This module provides a three-layer verification architecture following Anthropic best practices:
- Layer 1: Rules-based validation (input validation, business logic)
- Layer 2: Visual feedback (HTML structure, document quality)
- Layer 3: LLM-as-judge (analytical quality, Phase 2)

Design Principles:
- Per-bot configuration (lenient/strict/off modes)
- Warn-first approach (minimize false positives)
- Progressive enhancement (start lenient, tighten over time)
"""

from .config import VerificationConfig, VerificationMode
from .validators import (
    validate_inputs,
    ValidationError,
    ValidationWarning,
)
from .calculators import (
    safe_divide,
    safe_percentage,
    safe_multiply,
    CalculationError,
)
from .verifiers import (
    verify_financial_balance,
    verify_date_range,
    verify_positive_number,
    VerificationResult,
)
from .formatters import (
    format_currency,
    format_percentage,
    format_date,
    FormatError,
)
from .visual_verifiers import (
    verify_html_presentation,
    verify_document_formatting,
    verify_chart_quality,
    verify_visual_content,
)

__all__ = [
    # Configuration
    'VerificationConfig',
    'VerificationMode',
    # Validators
    'validate_inputs',
    'ValidationError',
    'ValidationWarning',
    # Calculators
    'safe_divide',
    'safe_percentage',
    'safe_multiply',
    'CalculationError',
    # Verifiers
    'verify_financial_balance',
    'verify_date_range',
    'verify_positive_number',
    'VerificationResult',
    # Formatters
    'format_currency',
    'format_percentage',
    'format_date',
    'FormatError',
    # Visual Verifiers
    'verify_html_presentation',
    'verify_document_formatting',
    'verify_chart_quality',
    'verify_visual_content',
]
