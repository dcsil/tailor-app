from io import BytesIO
from unittest.mock import patch, MagicMock
from datetime import datetime
from bson import ObjectId


def create_test_file(filename="test.jpg", content=b"Test content"):
    return (BytesIO(content), filename)


@patch("routes.file_routes.co.chat")
def test_analyze_file_success(mock_chat, client):
    mock_response = MagicMock()
    mock_response.message.content = [
        MagicMock(
            text='["Vibrant street fashion", "street style photograph", "red, black, white"]'
        )
    ]
    mock_chat.return_value = mock_response

    file, filename = create_test_file()

    response = client.post(
        "/api/files/analyze",
        data={"file": (file, filename)},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert (
        response_json["analysis"]
        == '["Vibrant street fashion", "street style photograph", "red, black, white"]'
    )

    mock_chat.assert_called_once()
    call_args = mock_chat.call_args[1]
    assert call_args["model"] == "c4ai-aya-vision-8b"
    assert call_args["temperature"] == 0


def test_analyze_file_no_file(client):
    response = client.post("/api/files/analyze", data={})
    assert response.status_code == 400
    assert "No file uploaded" in response.get_json()["error"]


@patch("routes.file_routes.co.chat")
def test_analyze_file_exception(mock_chat, client):
    mock_chat.side_effect = Exception("Cohere API error")

    file, filename = create_test_file()

    response = client.post(
        "/api/files/analyze",
        data={"file": (file, filename)},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert "error" in response_json
    assert "Cohere API error" in response_json["error"]


@patch("routes.file_routes.blob_storage.upload_file")
@patch("routes.file_routes.cohere.ClientV2.embed")
@patch("routes.file_routes.insert_document")
def test_upload_file_success(
    mock_insert_document, mock_embed, mock_upload_file, client
):
    mock_upload_file.return_value = {
        "blob_name": "test_blob",
        "blob_url": "http://example.com/test_blob",
        "size": 1234,
        "container": "test_container",
    }
    mock_embed.return_value.embeddings.float = [[0.1, 0.2, 0.3]]
    mock_insert_document.return_value = "document_id_123"

    file, filename = create_test_file()
    data = {
        "file": (file, filename),
        "description": "Test file description",
        "user_id": "user_123",
        "class": "art and film",
        "colour": "blue",
    }

    response = client.post(
        "/api/files/upload", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"]
    assert response_json["message"] == "File uploaded successfully"
    assert "file_data" in response_json
    assert response_json["file_data"]["document_id"] == "document_id_123"
    assert response_json["file_data"]["class"] == "art and film"
    assert response_json["file_data"]["colour"] == "blue"


def test_upload_file_no_file(client):
    response = client.post("/api/files/upload", data={})
    assert response.status_code == 400
    assert "No file part" in response.get_json()["error"]


def test_upload_file_empty_filename(client):
    file = BytesIO(b"")
    response = client.post(
        "/api/files/upload",
        data={"file": (file, "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "No selected file" in response.get_json()["error"]


def test_upload_file_invalid_extension(client):
    file, filename = create_test_file(filename="test.xyz")
    response = client.post(
        "/api/files/upload",
        data={"file": (file, filename), "user_id": "user_123"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "File type not allowed" in response.get_json()["error"]


def test_upload_file_missing_user_id(client):
    file, filename = create_test_file()
    response = client.post(
        "/api/files/upload",
        data={"file": (file, filename)},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "User ID is required" in response.get_json()["error"]


@patch("routes.file_routes.blob_storage.upload_file")
@patch("routes.file_routes.insert_document")
def test_upload_file_invalid_class(mock_insert_document, mock_upload_file, client):
    file, filename = create_test_file()
    data = {
        "file": (file, filename),
        "description": "Test file description",
        "user_id": "user_123",
        "class": "invalid_class",
        "colour": "blue",
    }

    response = client.post(
        "/api/files/upload", data=data, content_type="multipart/form-data"
    )
    print(response)
    assert response.status_code == 400
    response_json = response.get_json()
    assert "error" in response_json
    assert "Invalid class" in response_json["error"]

    mock_upload_file.assert_not_called()
    mock_insert_document.assert_not_called()


@patch("routes.file_routes.blob_storage.upload_file")
@patch("routes.file_routes.logger")
def test_upload_file_exception(mock_logger, mock_upload_file, client):
    mock_upload_file.side_effect = Exception("Storage service unavailable")

    file, filename = create_test_file()
    data = {
        "file": (file, filename),
        "description": "Test file description",
        "user_id": "user_123",
        "class": "art and film",
        "colour": "blue",
    }

    response = client.post(
        "/api/files/upload", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Storage service unavailable" in response_json["error"]

    mock_logger.error.assert_called_once()
    assert "Error in file upload" in mock_logger.error.call_args[0][0]
    assert mock_logger.error.call_args[1]["exc_info"] is True


@patch("routes.file_routes.find_documents")
def test_get_user_files_success(mock_find_documents, client):
    mock_find_documents.return_value = [
        {
            "_id": "1",
            "filename": "test1.jpg",
            "description": "Test file 1",
            "class": "fashion illustration",
            "colour": "red",
        },
        {
            "_id": "2",
            "filename": "test2.jpg",
            "description": "Test file 2",
            "class": "texture",
            "colour": "green",
        },
    ]

    response = client.get("/api/files/user/user_123")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"]
    assert response_json["count"] == 2
    assert len(response_json["files"]) == 2
    assert response_json["files"][0]["_id"] == "1"
    assert response_json["files"][0]["class"] == "fashion illustration"
    assert response_json["files"][0]["colour"] == "red"
    assert response_json["files"][1]["filename"] == "test2.jpg"
    assert response_json["files"][1]["class"] == "texture"
    assert response_json["files"][1]["colour"] == "green"


@patch("routes.file_routes.find_documents")
def test_get_user_files_exception(mock_find_documents, client):
    mock_find_documents.side_effect = Exception("Database connection error")
    response = client.get("/api/files/user/user_123")
    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]


@patch("routes.file_routes.find_documents")
def test_get_user_files_timestamp_formatting(mock_find_documents, client):
    test_time = datetime(2025, 3, 15, 10, 30, 45)
    mock_find_documents.return_value = [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "filename": "test.jpg",
            "description": "Test file",
            "timestamp": test_time,
            "class": "art and film",
            "colour": "blue",
        }
    ]

    response = client.get("/api/files/user/user_123")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert len(response_json["files"]) == 1

    assert response_json["files"][0]["timestamp"] == "2025-03-15T10:30:45"
    assert isinstance(response_json["files"][0]["timestamp"], str)


@patch("routes.file_routes.find_documents")
@patch("routes.file_routes.blob_storage.delete_blob")
@patch("routes.file_routes.delete_document")
def test_delete_file_success(
    mock_delete_document, mock_delete_blob, mock_find_documents, client
):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": file_id,
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "class": "nature",
            "colour": "blue",
        }
    ]
    mock_delete_blob.return_value = True

    response = client.delete(f"/api/files/1/{file_id}")

    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["success"]
    assert response_json["message"] == "File deleted successfully"

    mock_find_documents.assert_called_once_with(
        "1", "files", {"_id": ObjectId(file_id)}
    )
    mock_delete_blob.assert_called_once_with("blob123", "container1")
    mock_delete_document.assert_called_once_with("1", "files", file_id)


@patch("routes.file_routes.find_documents")
def test_delete_file_not_found(mock_find_documents, client):
    mock_find_documents.return_value = []
    response = client.delete("/api/files/user_123/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    assert "File not found" in response.get_json()["error"]


@patch("routes.file_routes.find_documents")
def test_delete_file_exception(mock_find_documents, client):
    mock_find_documents.side_effect = Exception("MongoDB connection error")
    response = client.delete("/api/files/user_123/507f1f77bcf86cd799439011")
    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "MongoDB connection error" in response_json["error"]


@patch("routes.file_routes.find_documents")
@patch("routes.file_routes.blob_storage.delete_blob")
@patch("routes.file_routes.delete_document")
@patch("routes.file_routes.logger")
def test_delete_file_blob_storage_failure(
    mock_logger, mock_delete_document, mock_delete_blob, mock_find_documents, client
):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": file_id,
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
        }
    ]
    mock_delete_blob.return_value = False

    response = client.delete(f"/api/files/user_123/{file_id}")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True

    mock_logger.warning.assert_called_once()
    assert "Could not delete blob" in mock_logger.warning.call_args[0][0]


@patch("routes.file_routes.find_documents")
@patch("routes.file_routes.blob_storage.update_blob")
@patch("routes.file_routes.update_document")
@patch("routes.file_routes.co.embed")
def test_update_file_success(
    mock_embed, mock_update_document, mock_update_blob, mock_find_documents, client
):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": file_id,
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "description": "Old description",
            "class": "runway",
            "colour": "black",
        }
    ]
    mock_update_blob.return_value = True
    mock_embed.return_value.embeddings.float = [[0.1, 0.2, 0.3]]
    mock_update_document.return_value = {
        "_id": file_id,
        "filename": "test.jpg",
        "description": "New description",
        "class": "street style photograph",
        "colour": "white",
        "embedding": [0.1, 0.2, 0.3],
    }

    response = client.patch(
        f"/api/files/1/{file_id}",
        data={
            "description": "New description",
            "class": "street style photograph",
            "colour": "white",
        },
    )

    assert response.status_code == 200

    response_json = response.get_json()
    assert response_json["success"]
    assert response_json["message"] == "File updated successfully"

    mock_find_documents.assert_called_once_with(
        "1", "files", {"_id": ObjectId(file_id)}
    )

    expected_updated_doc = {
        "_id": file_id,
        "filename": "test.jpg",
        "blob_name": "blob123",
        "container": "container1",
        "description": "New description",
        "class": "street style photograph",
        "colour": "white",
        "embedding": [0.1, 0.2, 0.3],
    }

    mock_update_blob.assert_called_once_with(
        "blob123", expected_updated_doc, "container1"
    )
    mock_update_document.assert_called_once_with(
        "1", "files", file_id, expected_updated_doc
    )
    mock_embed.assert_called_once_with(
        texts=["New description", "street style photograph", "white"],
        model="embed-english-v3.0",
        input_type="search_document",
        embedding_types=["float"],
    )


@patch("routes.file_routes.find_documents")
def test_update_file_invalid_class(mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": file_id,
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "description": "Old description",
            "class": "runway",
            "colour": "black",
        }
    ]

    response = client.patch(f"/api/files/1/{file_id}", data={"class": "invalid_class"})

    assert response.status_code == 400
    response_json = response.get_json()
    assert "error" in response_json
    assert "Invalid class" in response_json["error"]


@patch("routes.file_routes.find_documents")
def test_update_file_not_found(mock_find_documents, client):
    mock_find_documents.return_value = []
    response = client.patch("/api/files/user_123/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    assert "File not found" in response.get_json()["error"]


@patch("routes.file_routes.find_documents")
@patch("routes.file_routes.blob_storage.update_blob")
@patch("routes.file_routes.update_document")
@patch("routes.file_routes.co.embed")
@patch("routes.file_routes.logger")
def test_update_file_blob_storage_failure(
    mock_logger,
    mock_embed,
    mock_update_document,
    mock_update_blob,
    mock_find_documents,
    client,
):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": file_id,
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "description": "Old description",
            "class": "runway",
            "colour": "black",
        }
    ]

    mock_update_blob.return_value = False

    mock_embed.return_value.embeddings.float = [[0.1, 0.2, 0.3]]
    mock_update_document.return_value = {
        "_id": file_id,
        "filename": "test.jpg",
        "description": "New description",
        "class": "street style photograph",
        "colour": "white",
    }

    response = client.patch(
        f"/api/files/user_123/{file_id}",
        data={
            "description": "New description",
            "class": "street style photograph",
            "colour": "white",
        },
    )

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True

    mock_logger.warning.assert_called_once()
    assert "Could not update blob" in mock_logger.warning.call_args[0][0]
    assert "blob123" in mock_logger.warning.call_args[0][0]
    assert "container1" in mock_logger.warning.call_args[0][0]


@patch("routes.file_routes.find_documents")
@patch("routes.file_routes.logger")
def test_update_file_exception(mock_logger, mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.side_effect = Exception("Database connection error")

    response = client.patch(
        f"/api/files/user_123/{file_id}",
        data={
            "description": "New description",
            "class": "street style photograph",
            "colour": "white",
        },
    )

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]

    mock_logger.error.assert_called_once()
    assert "Error updating file" in mock_logger.error.call_args[0][0]
    assert mock_logger.error.call_args[1]["exc_info"] is True


@patch("routes.file_routes.find_documents")
def test_get_file_metadata_success(mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = [
        {
            "_id": ObjectId(file_id),
            "filename": "test.jpg",
            "blob_name": "blob123",
            "container": "container1",
            "description": "Test file description",
            "class": "street style photograph",
            "colour": "red",
        }
    ]

    response = client.get(f"/api/files/user_123/{file_id}")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True
    assert "file_data" in response_json

    file_data = response_json["file_data"]
    assert file_data["_id"] == file_id
    assert file_data["blob_name"] == "blob123"
    assert file_data["description"] == "Test file description"
    assert file_data["class"] == "street style photograph"
    assert file_data["colour"] == "red"


@patch("routes.file_routes.find_documents")
def test_get_file_metadata_not_found(mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.return_value = []

    response = client.get(f"/api/files/user_123/{file_id}")

    assert response.status_code == 404
    response_json = response.get_json()
    assert "error" in response_json
    assert "File not found" in response_json["error"]


@patch("routes.file_routes.find_documents")
def test_get_file_metadata_exception(mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    mock_find_documents.side_effect = Exception("Database connection error")

    response = client.get(f"/api/files/user_123/{file_id}")

    assert response.status_code == 500
    response_json = response.get_json()
    assert response_json["success"] is False
    assert "Database connection error" in response_json["error"]


@patch("routes.file_routes.find_documents")
def test_get_file_metadata_missing_fields(mock_find_documents, client):
    file_id = "507f1f77bcf86cd799439011"
    # Document with missing optional fields to test default values
    mock_find_documents.return_value = [
        {
            "_id": ObjectId(file_id),
            "filename": "test.jpg",
            "blob_name": "blob123",
            # Missing description, class, and colour
        }
    ]

    response = client.get(f"/api/files/user_123/{file_id}")

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["success"] is True

    file_data = response_json["file_data"]
    assert file_data["_id"] == file_id
    assert file_data["blob_name"] == "blob123"
    assert file_data["description"] == ""  # Default empty string
    assert file_data["class"] == ""  # Default empty string
    assert file_data["colour"] == ""  # Default empty string
