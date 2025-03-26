import pytest
import os
import sys

# Add the parent directory to sys.path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['COHERE_API_KEY'] = 'test_api_key'
os.environ['TESTING'] = 'True'

# Set environment variables for testing
@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Set up environment variables for testing."""

    # Add any other environment variables needed for tests
    yield

from app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client