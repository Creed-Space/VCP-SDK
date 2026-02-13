"""
Pytest configuration for VCP tests.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_vcp_token():
    """Sample VCP identity token for testing."""
    return "family.safe.guide@1.2.0"


@pytest.fixture
def sample_csm1():
    """Sample CSM1 persona specification for testing."""
    return "N5+F+E"


@pytest.fixture
def sample_context():
    """Sample VCP context for testing."""
    return {
        "time_of_day": "morning",
        "location": "home",
        "audience": "children",
    }
