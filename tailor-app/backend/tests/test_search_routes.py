from unittest.mock import patch

@patch('routes.search_routes.get_user_id') 
@patch('routes.search_routes.get_user_collection')  
@patch('routes.search_routes.search_database') 
def test_search_prompt_valid_request(mock_search, mock_get_collection, mock_get_user_id, client):
    mock_get_user_id.return_value = 'user123'
    mock_get_collection.return_value = "mocked_files_collection"
    mock_search.return_value = ['image_1', 'image_2', 'image_3']

    response = client.post('/api/search-prompt', json={"prompt": "fashion"})
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['image_ids'] == ['image_1', 'image_2', 'image_3']
    assert response_data['user_id'] == 'user123'