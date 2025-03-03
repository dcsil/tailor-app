import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test the home endpoint returns the expected response."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello, World!" in response.data

def test_health_check(client):
    """Test the health check endpoint returns status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

@patch('app.co.chat')
def test_generate_response_basic_chat(mock_chat, client):
    """Test the generate response endpoint with basic_chat template."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.message.content = [MagicMock(text="This is a test response")]
    mock_chat.return_value = mock_response
    
    # Test data
    test_data = {
        'prompt': 'Hello, how are you?',
        'template': 'basic_chat'
    }
    
    # Send request
    response = client.post('/api/generate',
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert data['response'] == "This is a test response"
    
    # Check that Cohere client was called with correct parameters
    mock_chat.assert_called_once()
    args, kwargs = mock_chat.call_args
    assert kwargs['model'] == "command-r-08-2024"
    assert kwargs['messages'][0]['role'] == "system"
    assert kwargs['messages'][0]['content'] == "You are a helpful fashion assistant."
    assert kwargs['messages'][1]['content'] == "Hello, how are you?"
    assert kwargs['temperature'] == 0.7
    assert kwargs['max_tokens'] == 300

@patch('app.co.chat')
def test_generate_response_expert_mode(mock_chat, client):
    """Test the generate response endpoint with expert_mode template."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.message.content = [MagicMock(text="This is an expert response")]
    mock_chat.return_value = mock_response
    
    # Test data
    test_data = {
        'prompt': 'How do I implement unit tests?',
        'template': 'expert_mode'
    }
    
    # Send request
    response = client.post('/api/generate',
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert data['response'] == "This is an expert response"
    
    # Check that Cohere client was called with correct parameters
    mock_chat.assert_called_once()
    args, kwargs = mock_chat.call_args
    assert kwargs['model'] == "command-r-08-2024"
    assert kwargs['messages'][0]['role'] == "system"
    assert kwargs['messages'][0]['content'] == "You are an expert programmer focused on providing technical solutions."
    assert kwargs['temperature'] == 0.3
    assert kwargs['max_tokens'] == 500

@patch('app.co.chat')
def test_generate_response_error(mock_chat, client):
    """Test the generate response endpoint when an error occurs."""
    # Configure the mock to raise an exception
    mock_chat.side_effect = Exception("Test error")
    
    # Test data
    test_data = {
        'prompt': 'Hello, how are you?',
        'template': 'basic_chat'
    }
    
    # Send request
    response = client.post('/api/generate',
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert "Test error" in data['error']

def test_generate_response_invalid_template(client):
    """Test the generate response endpoint with an invalid template."""
    # Test data
    test_data = {
        'prompt': 'Hello, how are you?',
        'template': 'nonexistent_template'
    }
    
    # Send request
    response = client.post('/api/generate',
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data