"""
Pytest configuration for Projects Service integration tests
"""
import pytest

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Projects service"""
    return "http://localhost:8007"

@pytest.fixture(scope="session")
def api_prefix():
    """API prefix for Projects endpoints"""
    return "/api/projects"
