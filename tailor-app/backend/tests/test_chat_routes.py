from unittest.mock import patch, MagicMock

from flask import json


@patch("routes.chat_routes.co.chat")
def test_generate_response_basic_chat(mock_chat, client):
    """Test the generate response endpoint with basic_chat template."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.message.content = [MagicMock(text="This is a test response")]
    mock_chat.return_value = mock_response

    # Test data
    test_data = {"prompt": "Hello, how are you?", "template": "basic_chat"}

    # Send request
    response = client.post(
        "/api/generate", data=json.dumps(test_data), content_type="application/json"
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "response" in data
    assert data["response"] == "This is a test response"

    # Check that Cohere client was called with correct parameters
    mock_chat.assert_called_once()
    _, kwargs = mock_chat.call_args
    assert kwargs["model"] == "command-r-08-2024"
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == "You are a helpful fashion assistant."
    assert kwargs["messages"][1]["content"] == "Hello, how are you?"
    assert kwargs["temperature"] == 0.7
    assert kwargs["max_tokens"] == 300


@patch("routes.chat_routes.co.chat")
def test_generate_response_expert_mode(mock_chat, client):
    """Test the generate response endpoint with expert_mode template."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.message.content = [MagicMock(text="This is an expert response")]
    mock_chat.return_value = mock_response

    # Test data
    test_data = {"prompt": "How do I implement unit tests?", "template": "expert_mode"}

    # Send request
    response = client.post(
        "/api/generate", data=json.dumps(test_data), content_type="application/json"
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "response" in data
    assert data["response"] == "This is an expert response"

    # Check that Cohere client was called with correct parameters
    mock_chat.assert_called_once()
    _, kwargs = mock_chat.call_args
    assert kwargs["model"] == "command-r-08-2024"
    assert kwargs["messages"][0]["role"] == "system"
    assert (
        kwargs["messages"][0]["content"]
        == "You are an expert programmer focused on providing technical solutions."
    )
    assert kwargs["temperature"] == 0.3
    assert kwargs["max_tokens"] == 500


@patch("routes.chat_routes.co.chat")
def test_generate_response_error(mock_chat, client):
    """Test the generate response endpoint when an error occurs."""
    # Configure the mock to raise an exception
    mock_chat.side_effect = Exception("Test error")

    # Test data
    test_data = {"prompt": "Hello, how are you?", "template": "basic_chat"}

    # Send request
    response = client.post(
        "/api/generate", data=json.dumps(test_data), content_type="application/json"
    )

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Test error" in data["error"]


@patch("routes.chat_routes.find_documents")
@patch("routes.chat_routes.get_user_id")
def test_get_history_success(mock_get_user_id, mock_find_documents, client):
    """Test the get_history endpoint when it successfully retrieves history."""
    # Mock the user ID
    mock_get_user_id.return_value = "test_user_123"

    # Create mock conversations with MongoDB-like structure
    mock_conversations = [
        {
            "_id": "conv_id_1",
            "prompt": "Hello, how are you?",
            "template": "basic_chat",
            "response": "I'm doing well, thanks for asking!",
            "timestamp": 1617120000,
        },
        {
            "_id": "conv_id_2",
            "prompt": "How do I implement tests?",
            "template": "expert_mode",
            "response": "Here's how you implement tests...",
            "timestamp": 1617110000,
        },
    ]

    # Set up the mock for find_documents to return a mock cursor
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value.limit.return_value = mock_conversations
    mock_find_documents.return_value = mock_cursor

    # Send request
    response = client.get("/api/history")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]["_id"] == "conv_id_1"
    assert data[1]["_id"] == "conv_id_2"

    # Verify our mocks were called correctly
    mock_get_user_id.assert_called_once()
    mock_find_documents.assert_called_once_with("test_user_123", "conversations", {})
    mock_cursor.sort.assert_called_once_with("timestamp", -1)
    mock_cursor.sort.return_value.limit.assert_called_once_with(10)


@patch("routes.chat_routes.find_documents")
@patch("routes.chat_routes.get_user_id")
def test_get_history_empty(mock_get_user_id, mock_find_documents, client):
    """Test the get_history endpoint when no conversations exist."""
    # Mock the user ID
    mock_get_user_id.return_value = "test_user_with_no_history"

    # Set up the mock for find_documents to return an empty list
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value.limit.return_value = []
    mock_find_documents.return_value = mock_cursor

    # Send request
    response = client.get("/api/history")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0
    assert isinstance(data, list)

    # Verify our mocks were called correctly
    mock_get_user_id.assert_called_once()
    mock_find_documents.assert_called_once_with(
        "test_user_with_no_history", "conversations", {}
    )


@patch("routes.chat_routes.find_documents")
@patch("routes.chat_routes.get_user_id")
def test_get_history_error(mock_get_user_id, mock_find_documents, client):
    """Test the get_history endpoint when an error occurs."""
    # Configure the mocks to raise exceptions
    mock_get_user_id.side_effect = Exception("User ID error")

    # Send request
    response = client.get("/api/history")

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "User ID error" in data["error"]

    # Verify our mock was called
    mock_get_user_id.assert_called_once()
    # find_documents should not be called if get_user_id fails
    mock_find_documents.assert_not_called()


@patch("routes.chat_routes.find_documents")
@patch("routes.chat_routes.get_user_id")
def test_get_history_database_error(mock_get_user_id, mock_find_documents, client):
    """Test the get_history endpoint when a database error occurs."""
    # Mock the user ID
    mock_get_user_id.return_value = "test_user_123"

    # Configure the mock to raise a database exception
    mock_find_documents.side_effect = Exception("Database connection error")

    # Send request
    response = client.get("/api/history")

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Database connection error" in data["error"]

    # Verify our mocks were called correctly
    mock_get_user_id.assert_called_once()
    mock_find_documents.assert_called_once_with("test_user_123", "conversations", {})
