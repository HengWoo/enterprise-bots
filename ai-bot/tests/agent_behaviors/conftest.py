"""
Pytest fixtures for agent behavior tests.

Provides reusable fixtures for creating test agents, mock data,
and test utilities.
"""

import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any

# Test fixtures will be added as needed during pilot validation
# Start minimal - only what's required for critical path tests

@pytest.fixture
def test_data_dir():
    """Directory containing test data files."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing calculations."""
    return [
        {"date": "2025-01-01", "revenue": 1000.0, "cost": 600.0},
        {"date": "2025-01-02", "revenue": 1200.0, "cost": 700.0},
        {"date": "2025-01-03", "revenue": 900.0, "cost": 500.0},
    ]

@pytest.fixture
def sample_operations_data():
    """Sample operations data for testing analytics."""
    return [
        {"id": 1, "status": "completed", "created_at": "2025-01-01", "value": 100.0},
        {"id": 2, "status": "in_progress", "created_at": "2025-01-02", "value": 150.0},
        {"id": 3, "status": "completed", "created_at": "2025-01-03", "value": 120.0},
    ]
