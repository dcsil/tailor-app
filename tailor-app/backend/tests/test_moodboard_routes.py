from io import BytesIO
from unittest.mock import patch, MagicMock
from datetime import datetime
from bson import ObjectId


def create_test_board(filename="test_board.jpg", content=b"Test board content"):
    return (BytesIO(content), filename)


def create_test_image(filename="test_image.jpg", content=b"Test image content"):
    return (BytesIO(content), filename)


@patch("routes.moodboard_routes.blob_storage.upload_file")
@patch("routes.moodboard_routes.insert_document")
@patch("routes.moodboard_routes.find_documents")
@patch("routes.moodboard_routes.delete_document")
def test_insert_moodboard_success(
    mock_delete_document,
    mock_find_documents,
    mock_insert_document,
    mock_upload_file,
    client,
):
    # Setup mock responses
    mock_upload_file.return_value = {
        "blob_name": "test_blob",
        "blob_url": "http://example.com/test_blob",
        "size": 1234,
        "container": "test_container",
    }
    mock_insert_document.return_value = "document_id_123"
    mock_find_documents.return_value = [
        {"_id": ObjectId("507f1f77bcf86cd799439011"), "prompt": "test prompt"}
    ]

    # Create test data
    board, filename = create_test_board()
    data = {
        "file": (board, filename),
        "user_id": "user_123",
        "image_ids": "img1,img2,img3",
        "prompt": "test prompt",
    }

    # Make request
    response = client.post(
        "/api/boards/upload", data=data, content_type="multipart/form-data"
    )

    # Assert response
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert response_json["message"] == "Board exported successfully"
    assert "board_data" in response_json
    assert response_json["board_data"]["document_id"] == "document_id_123"
    assert response_json["board_data"]["original_boardname"] == "test_board.jpg"

    # Assert mocks were called correctly
    mock_find_documents.assert_called_once_with(
        "user_123", "temp_boards", {"prompt": "test prompt"}
    )
    mock_delete_document.assert_called_once_with(
        "user_123", "temp_boards", "507f1f77bcf86cd799439011"
    )


def test_insert_moodboard_no_board(client):
    response = client.post("/api/boards/upload", data={})
    assert response.status_code == 400
    assert "No board provided" in response.get_json()["error"]


def test_insert_moodboard_empty_filename(client):
    board = BytesIO(b"")
    response = client.post(
        "/api/boards/upload",
        data={"file": (board, "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "No selected board" in response.get_json()["error"]


def test_insert_moodboard_invalid_extension(client):
    board, filename = create_test_board(filename="test.xyz")
    response = client.post(
        "/api/boards/upload",
        data={"file": (board, filename), "user_id": "user_123"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "Board type not allowed" in response.get_json()["error"]


def test_insert_moodboard_missing_user_id(client):
    board, filename = create_test_board()
    response = client.post(
        "/api/boards/upload",
        data={"file": (board, filename)},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "User ID is required" in response.get_json()["error"]


@patch("routes.moodboard_routes.blob_storage.upload_file")
@patch("routes.moodboard_routes.logger")
def test_insert_moodboard_exception(mock_logger, mock_upload_file, client):
    mock_upload_file.side_effect = Exception("Storage service unavailable")

    board, filename = create_test_board()
    data = {
        "file": (board, filename),
        "user_id": "user_123",
        "image_ids": "img1,img2,img3",
        "prompt": "test prompt",
    }

    response = client.post(
        "/api/boards/upload", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Storage service unavailable" in response_json["error"]

    mock_logger.error.assert_called_once()
    assert "Error in board upload" in mock_logger.error.call_args[0][0]
    assert mock_logger.error.call_args[1]["exc_info"] is True


@patch("routes.moodboard_routes.find_documents")
def test_get_moodboards_success(mock_find_documents, client):
    test_time = datetime(2025, 3, 15, 10, 30, 45)
    mock_find_documents.return_value = [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "boardname": "test_board.jpg",
            "blob_url": "http://example.com/test_blob",
            "image_ids": "img1,img2,img3",
            "timestamp": test_time,
            "prompt": "summer fashion inspiration",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439022"),
            "boardname": "test_board2.jpg",
            "blob_url": "http://example.com/test_blob2",
            "image_ids": "img4,img5,img6",
            "timestamp": test_time,
            "prompt": "winter fashion ideas",
        },
    ]

    response = client.get("/api/boards/user/user_123")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert response_json["count"] == 2
    assert len(response_json["boards"]) == 2
    assert response_json["boards"][0]["_id"] == "507f1f77bcf86cd799439011"
    assert response_json["boards"][0]["prompt"] == "summer fashion inspiration"
    assert response_json["boards"][0]["timestamp"] == "2025-03-15T10:30:45"
    assert response_json["boards"][1]["boardname"] == "test_board2.jpg"
    assert response_json["boards"][1]["prompt"] == "winter fashion ideas"


@patch("routes.moodboard_routes.find_documents")
def test_get_moodboards_exception(mock_find_documents, client):
    mock_find_documents.side_effect = Exception("Database connection error")

    response = client.get("/api/boards/user/user_123")

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]


@patch("routes.moodboard_routes.find_documents")
@patch("routes.moodboard_routes.blob_storage.delete_blob")
@patch("routes.moodboard_routes.delete_document")
def test_delete_moodboard_success(
    mock_delete_document, mock_delete_blob, mock_find_documents, client
):
    board_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": ObjectId(board_id),
            "boardname": "test_board.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "image_ids": "img1,img2,img3",
            "prompt": "summer fashion inspiration",
        }
    ]
    mock_delete_blob.return_value = True

    response = client.delete(f"/api/boards/user_123/{board_id}")

    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["success"] is True
    assert response_json["message"] == "Board deleted successfully"

    mock_find_documents.assert_called_once_with(
        "user_123", "boards", {"_id": ObjectId(board_id)}
    )
    mock_delete_blob.assert_called_once_with("blob123", "container1")
    mock_delete_document.assert_called_once_with("user_123", "boards", board_id)


@patch("routes.moodboard_routes.find_documents")
def test_delete_moodboard_not_found(mock_find_documents, client):
    mock_find_documents.return_value = []
    board_id = "507f1f77bcf86cd799439011"

    response = client.delete(f"/api/boards/user_123/{board_id}")

    assert response.status_code == 404
    assert "Board not found" in response.get_json()["error"]


@patch("routes.moodboard_routes.find_documents")
def test_delete_moodboard_exception(mock_find_documents, client):
    mock_find_documents.side_effect = Exception("Database connection error")
    board_id = "507f1f77bcf86cd799439011"

    response = client.delete(f"/api/boards/user_123/{board_id}")

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]


@patch("routes.moodboard_routes.find_documents")
@patch("routes.moodboard_routes.blob_storage.delete_blob")
@patch("routes.moodboard_routes.delete_document")
@patch("routes.moodboard_routes.logger")
def test_delete_moodboard_blob_storage_failure(
    mock_logger, mock_delete_document, mock_delete_blob, mock_find_documents, client
):
    board_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": ObjectId(board_id),
            "boardname": "test_board.jpg",
            "blob_name": "blob123",
            "container": "container1",
        }
    ]
    mock_delete_blob.return_value = False

    response = client.delete(f"/api/boards/user_123/{board_id}")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True

    mock_logger.warning.assert_called_once()
    assert "Could not delete blob" in mock_logger.warning.call_args[0][0]
    assert "blob123" in mock_logger.warning.call_args[0][0]
    assert "container1" in mock_logger.warning.call_args[0][0]


@patch("routes.moodboard_routes.find_documents")
@patch("routes.moodboard_routes.delete_document")
def test_delete_temp_moodboard_success(
    mock_delete_document, mock_find_documents, client
):
    prompt = "summer%20fashion%20inspiration"
    mock_find_documents.return_value = [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "prompt": "summer fashion inspiration",
            "image_ids": "img1,img2,img3",
        }
    ]

    response = client.delete(f"/api/temp_boards/user_123/{prompt}")

    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["success"] is True
    assert response_json["message"] == "Temp board deleted successfully"

    mock_find_documents.assert_called_once_with(
        "user_123", "temp_boards", {"prompt": "summer fashion inspiration"}
    )
    mock_delete_document.assert_called_once_with(
        "user_123", "temp_boards", "507f1f77bcf86cd799439011"
    )


@patch("routes.moodboard_routes.find_documents")
def test_delete_temp_moodboard_not_found(mock_find_documents, client):
    prompt = "nonexistent%20prompt"
    mock_find_documents.return_value = []

    response = client.delete(f"/api/temp_boards/user_123/{prompt}")

    assert response.status_code == 200
    assert "No temp boards to delete" in response.get_json()["message"]


@patch("routes.moodboard_routes.find_documents")
def test_delete_temp_moodboard_empty_result(mock_find_documents, client):
    prompt = "test%20prompt"
    mock_find_documents.return_value = [None]

    response = client.delete(f"/api/temp_boards/user_123/{prompt}")

    assert response.status_code == 404
    assert "Board not found" in response.get_json()["error"]


@patch("routes.moodboard_routes.find_documents")
def test_delete_temp_moodboard_exception(mock_find_documents, client):
    prompt = "summer%20fashion%20inspiration"
    mock_find_documents.side_effect = Exception("Database connection error")

    response = client.delete(f"/api/temp_boards/user_123/{prompt}")

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]


@patch("routes.moodboard_routes.co.chat")
def test_analyze_moodboard_success(mock_cohere_chat, client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.message.content = [
        MagicMock(text="# Moodboard Analysis\n\nThis is a test analysis")
    ]
    mock_cohere_chat.return_value = mock_response

    # Create test data
    image, filename = create_test_image()
    data = {
        "file": (image, filename),
    }

    # Make request
    response = client.post(
        "/api/boards/nodescriptionsanalyze",
        data=data,
        content_type="multipart/form-data",
    )

    # Assert response
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert (
        response_json["analysis"] == "# Moodboard Analysis\n\nThis is a test analysis"
    )

    # Verify the Cohere API was called with the correct parameters
    mock_cohere_chat.assert_called_once()
    call_args = mock_cohere_chat.call_args[1]
    assert call_args["model"] == "c4ai-aya-vision-8b"
    assert not call_args["temperature"]


def test_analyze_moodboard_no_file(client):
    response = client.post("/api/boards/nodescriptionsanalyze", data={})
    assert response.status_code == 400
    assert "No file uploaded" in response.get_json()["error"]


def test_analyze_moodboard_empty_file(client):
    response = client.post(
        "/api/boards/nodescriptionsanalyze",
        data={"file": (BytesIO(b""), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "No file received" in response.get_json()["error"]


@patch("routes.moodboard_routes.allowed_file")
def test_analyze_moodboard_invalid_file_format(mock_allowed_file, client):
    mock_allowed_file.return_value = False

    image, filename = create_test_image()
    data = {"file": (image, filename)}

    response = client.post(
        "/api/boards/nodescriptionsanalyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Unsupported file format" in response.get_json()["error"]


# @patch("routes.moodboard_routes.allowed_file")
# def test_analyze_moodboard_file_too_large(mock_allowed_file, client):
#     mock_allowed_file.return_value = True

#     # Create test image with content_length property
#     image, filename = create_test_image()
#     image.content_length = 30 * 1024 * 1024  # 30MB, should exceed MAX_IMAGE_SIZE

#     data = {"file": (image, filename)}

#     response = client.post(
#         "/api/boards/nodescriptionsanalyze",
#         data=data,
#         content_type="multipart/form-data",
#     )

#     assert response.status_code == 400
#     assert "File size exceeds 20 MB" in response.get_json()["error"]


@patch("routes.moodboard_routes.allowed_file")
@patch("routes.moodboard_routes.co.chat")
def test_analyze_moodboard_exception(mock_cohere_chat, mock_allowed_file, client):
    mock_allowed_file.return_value = True
    mock_cohere_chat.side_effect = Exception("AI service unavailable")

    image, filename = create_test_image()
    data = {"file": (image, filename)}

    response = client.post(
        "/api/boards/nodescriptionsanalyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert "AI service unavailable" in response_json["error"]


# Tests for analyze_moodboardV2 (with descriptions)
@patch("routes.moodboard_routes.co.chat")
def test_analyze_moodboardV2_success(mock_cohere_chat, client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.message.content = [
        MagicMock(
            text="# Detailed Moodboard Analysis\n\nThis is a detailed test analysis"
        )
    ]
    mock_cohere_chat.return_value = mock_response

    # Create test data
    image, filename = create_test_image()
    data = {
        "file": (image, filename),
        "image_descriptions": '["Image 1 description", "Image 2 description"]',
    }

    # Make request
    response = client.post(
        "/api/boards/analyze", data=data, content_type="multipart/form-data"
    )

    # Assert response
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert (
        response_json["analysis"]
        == "# Detailed Moodboard Analysis\n\nThis is a detailed test analysis"
    )

    # Verify the Cohere API was called with the correct parameters
    mock_cohere_chat.assert_called_once()
    call_args = mock_cohere_chat.call_args[1]
    assert call_args["model"] == "c4ai-aya-vision-8b"


def test_analyze_moodboardV2_no_file(client):
    response = client.post("/api/boards/analyze", data={})
    assert response.status_code == 400
    assert "No file uploaded" in response.get_json()["error"]


def test_analyze_moodboardV2_empty_file(client):
    response = client.post(
        "/api/boards/analyze",
        data={"file": (BytesIO(b""), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "No file selected" in response.get_json()["error"]


@patch("routes.moodboard_routes.allowed_file")
def test_analyze_moodboardV2_invalid_file_format(mock_allowed_file, client):
    mock_allowed_file.return_value = False

    image, filename = create_test_image()
    data = {"file": (image, filename)}

    response = client.post(
        "/api/boards/analyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Unsupported file format" in response.get_json()["error"]


# @patch("routes.moodboard_routes.allowed_file")
# def test_analyze_moodboardV2_file_too_large(mock_allowed_file, client):
#     mock_allowed_file.return_value = True

#     # Create test image with content_length property
#     image, filename = create_test_image()
#     image.content_length = 30 * 1024 * 1024  # 30MB, should exceed MAX_IMAGE_SIZE

#     data = {"file": (image, filename)}

#     response = client.post(
#         "/api/boards/analyze",
#         data=data,
#         content_type="multipart/form-data",
#     )

#     assert response.status_code == 400
#     assert "File size exceeds 20 MB" in response.get_json()["error"]


def test_analyze_moodboardV2_invalid_image_descriptions_format(client):
    image, filename = create_test_image()
    data = {"file": (image, filename), "image_descriptions": "invalid json format"}

    response = client.post(
        "/api/boards/analyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Invalid image_descriptions format" in response.get_json()["error"]


def test_analyze_moodboardV2_invalid_image_descriptions_type(client):
    image, filename = create_test_image()
    data = {
        "file": (image, filename),
        "image_descriptions": '{"not_a_list": "This is an object, not a list"}',
    }

    response = client.post(
        "/api/boards/analyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "image_descriptions must be a list" in response.get_json()["error"]


@patch("routes.moodboard_routes.allowed_file")
@patch("routes.moodboard_routes.co.chat")
def test_analyze_moodboardV2_exception(mock_cohere_chat, mock_allowed_file, client):
    mock_allowed_file.return_value = True
    mock_cohere_chat.side_effect = Exception("AI service unavailable")

    image, filename = create_test_image()
    data = {
        "file": (image, filename),
        "image_descriptions": '["Image 1 description", "Image 2 description"]',
    }

    response = client.post(
        "/api/boards/analyze",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert "Internal Server Error" in response_json["error"]
    assert "AI service unavailable" in response_json["details"]
