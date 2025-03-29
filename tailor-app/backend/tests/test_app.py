import json


def test_health_check(client):
    """Test the health check endpoint returns status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


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