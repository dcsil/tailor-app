import pytest
from unittest.mock import patch, MagicMock
from flask import json
from bson import ObjectId


@patch('routes.pin_routes.insert_document')
@patch('routes.pin_routes.get_user_id')
def test_insert_pin(mock_get_user_id, mock_insert_document, client):
    """Test the insert_pin route."""
    mock_get_user_id.return_value = "user_123"
    mock_insert_document.return_value = "pin_123"
    pin_data = {"description": "Test Pin"}
    response = client.post('/api/insert-pin', json=pin_data)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Ensure that the response has the expected pin_id (as a string)
    assert data['pin_id'] == "pin_123"
    assert data['user_id'] == "user_123"
    mock_get_user_id.assert_called_once()
    mock_insert_document.assert_called_once_with("user_123", "pins", pin_data)

@patch('routes.pin_routes.insert_documents')
@patch('routes.pin_routes.get_user_id')
def test_insert_pins(mock_get_user_id, mock_insert_documents, client):
    """Test the insert_pins route."""
    mock_get_user_id.return_value = "user_123"
    mock_insert_documents.return_value = ["pin_123", "pin_124"]

    pins_data = [{"url": "http://example1.com", "description": "Test Pin 1"}, {"url": "http://example2.com", "description": "Test Pin 2"}]
    response = client.post('/api/insert-pins', json=pins_data)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['pin_ids']) == 2
    assert data['pin_ids'] == ["pin_123", "pin_124"]
    assert data['user_id'] == "user_123"
    
    mock_get_user_id.assert_called_once()
    mock_insert_documents.assert_called_once_with("user_123", "pins", pins_data)

@patch('routes.pin_routes.delete_document')
@patch('routes.pin_routes.get_user_id')
def test_delete_pin(mock_get_user_id, mock_delete_document, client):
    """Test the delete_pin route."""
    mock_get_user_id.return_value = "user_123"
    
    pin_id = "pin_123"
    response = client.delete('/api/delete-pin', json=pin_id)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['pin_id'] == pin_id
    assert data['user_id'] == "user_123"
    
    mock_get_user_id.assert_called_once()
    mock_delete_document.assert_called_once_with("user_123", "pins", pin_id)

@patch('routes.pin_routes.delete_documents')
@patch('routes.pin_routes.get_user_id')
def test_delete_pins(mock_get_user_id, mock_delete_documents, client):
    """Test the delete_pins route."""
    mock_get_user_id.return_value = "user_123"
    
    pin_ids = ["pin_123", "pin_124"]
    response = client.delete('/api/delete-pins', json=pin_ids)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['pin_ids'] == pin_ids
    assert data['user_id'] == "user_123"
    
    mock_get_user_id.assert_called_once()
    mock_delete_documents.assert_called_once_with("user_123", "pins", pin_ids)

@patch('routes.pin_routes.update_document')
@patch('routes.pin_routes.get_user_id')
def test_update_pin(mock_get_user_id, mock_update_document, client):
    """Test the update_pin route."""
    mock_get_user_id.return_value = "user_123"
    
    pin_id = "pin_123"
    pin_data = {"description": "Updated Pin Description"}
    response = client.patch('/api/update-pin', json=pin_data, query_string={'pin_id': pin_id})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['pin_id'] == pin_id
    assert data['data'] == pin_data
    assert data['user_id'] == "user_123"
    
    mock_get_user_id.assert_called_once()
    mock_update_document.assert_called_once_with("user_123", "pins", pin_id, pin_data)

@patch('routes.pin_routes.find_documents')
@patch('routes.pin_routes.get_user_id')
def test_get_pins(mock_get_user_id, mock_find_documents, client):
    """Test the get_pins route."""
    mock_get_user_id.return_value = "user_123"
    mock_find_documents.return_value = [{"_id": "pin_123", "url": "http://example.com", "description": "Test Pin"}]
    
    response = client.get('/api/get-pins')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'pins' in data
    assert len(data['pins']) == 1
    assert data['pins'][0]['_id'] == "pin_123"
    
    mock_get_user_id.assert_called_once()
    mock_find_documents.assert_called_once_with("user_123", "pins", {})
