"""Pytest configuration and shared fixtures."""
import pytest


@pytest.fixture
def sample_data():
    """Sample data fixture for testing."""
    return {
        "time": list(range(10)),
        "values": [i**2 for i in range(10)],
    }


@pytest.fixture
def random_seed():
    """Fixed random seed for reproducible tests."""
    return 42
