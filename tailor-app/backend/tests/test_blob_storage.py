import unittest
from unittest.mock import patch, MagicMock
import os
import io

# Import the class to test
from utils.blob_storage import AzureBlobStorage


class TestAzureBlobStorage(unittest.TestCase):
    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_init_success(self, mock_blob_service_client):
        # Test successful initialization
        storage = AzureBlobStorage()

        # Verify BlobServiceClient was created with correct connection string
        mock_blob_service_client.from_connection_string.assert_called_once_with(
            "test_connection_string"
        )

        # Verify default container is set correctly
        self.assertEqual(storage.default_container, "user-uploads")

    @patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": ""})
    @patch("utils.blob_storage.BlobServiceClient")
    def test_init_missing_connection_string(self, mock_blob_service_client):
        # Test initialization fails when connection string is missing
        with self.assertRaises(ValueError) as context:
            AzureBlobStorage()

        self.assertIn(
            "Azure Storage connection string not configured", str(context.exception)
        )

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_get_container_client_default(self, mock_blob_service_client):
        # Test getting container client with default container
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        storage = AzureBlobStorage()
        storage.get_container_client()

        # Verify correct container was requested
        mock_service_client.get_container_client.assert_called_once_with("user-uploads")

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_get_container_client_specified(self, mock_blob_service_client):
        # Test getting container client with specified container
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        storage = AzureBlobStorage()
        storage.get_container_client("custom-container")

        # Verify correct container was requested
        mock_service_client.get_container_client.assert_called_once_with(
            "custom-container"
        )

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    @patch("utils.blob_storage.uuid.uuid4")
    def test_upload_file_success(self, mock_uuid, mock_blob_service_client):
        # Setup mocks
        mock_uuid.return_value = "test-uuid"

        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_container_client = MagicMock()
        mock_container_client.url = (
            "https://test-storage.blob.core.windows.net/user-uploads"
        )
        mock_container_client.container_name = "user-uploads"
        mock_service_client.get_container_client.return_value = mock_container_client

        # Create test file data
        file_data = io.BytesIO(b"test file content")
        file_content = file_data.getvalue()
        original_filename = "test_image.jpg"

        # Test upload_file method
        storage = AzureBlobStorage()
        result = storage.upload_file(file_content, original_filename)

        # Verify correct blob name was generated and upload was called
        expected_blob_name = "test-uuid.jpg"
        mock_container_client.upload_blob.assert_called_once_with(
            name=expected_blob_name, data=file_content, overwrite=True
        )

        # Verify returned data is correct
        self.assertEqual(result["blob_name"], expected_blob_name)
        self.assertEqual(
            result["blob_url"],
            f"https://test-storage.blob.core.windows.net/user-uploads/{expected_blob_name}",
        )
        self.assertEqual(result["container"], "user-uploads")
        self.assertEqual(result["size"], len(file_content))

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_upload_file_exception(self, mock_blob_service_client):
        # Setup mocks
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_container_client = MagicMock()
        mock_container_client.upload_blob.side_effect = Exception("Upload failed")
        mock_service_client.get_container_client.return_value = mock_container_client

        # Test upload_file method with exception
        storage = AzureBlobStorage()

        with self.assertRaises(Exception) as context:
            storage.upload_file(b"test content", "test.jpg")

        self.assertIn("Upload failed", str(context.exception))

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_delete_blob_success(self, mock_blob_service_client):
        # Setup mocks
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_container_client = MagicMock()
        mock_service_client.get_container_client.return_value = mock_container_client

        # Test delete_blob method
        storage = AzureBlobStorage()
        result = storage.delete_blob("test-blob.jpg")

        # Verify delete_blob was called with correct name
        mock_container_client.delete_blob.assert_called_once_with("test-blob.jpg")

        # Verify result is True for successful deletion
        self.assertTrue(result)

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_delete_blob_exception(self, mock_blob_service_client):
        # Setup mocks
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_container_client = MagicMock()
        mock_container_client.delete_blob.side_effect = Exception("Delete failed")
        mock_service_client.get_container_client.return_value = mock_container_client

        # Test delete_blob method with exception
        storage = AzureBlobStorage()
        result = storage.delete_blob("test-blob.jpg")

        # Verify result is False when deletion fails
        self.assertFalse(result)

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_update_blob_success(self, mock_blob_service_client):
        # Setup mocks
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_blob_client = MagicMock()
        mock_container_client = MagicMock()
        mock_container_client.get_blob_client.return_value = mock_blob_client
        mock_service_client.get_container_client.return_value = mock_container_client

        # Test data
        blob_name = "test-blob.jpg"
        new_data = {"description": "updated description"}

        # Test update_blob method
        storage = AzureBlobStorage()
        result = storage.update_blob(blob_name, new_data)

        # Verify get_blob_client was called with correct name
        mock_container_client.get_blob_client.assert_called_once_with(blob_name)

        # Verify upload_blob was called with correct data and overwrite flag
        mock_blob_client.upload_blob.assert_called_once_with(new_data, overwrite=True)

        # Verify result is True for successful update
        self.assertTrue(result)

    @patch.dict(
        os.environ, {"AZURE_STORAGE_CONNECTION_STRING": "test_connection_string"}
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_update_blob_exception(self, mock_blob_service_client):
        # Setup mocks
        mock_service_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = (
            mock_service_client
        )

        mock_blob_client = MagicMock()
        mock_blob_client.upload_blob.side_effect = Exception("Update failed")

        mock_container_client = MagicMock()
        mock_container_client.get_blob_client.return_value = mock_blob_client
        mock_service_client.get_container_client.return_value = mock_container_client

        # Test update_blob method with exception
        storage = AzureBlobStorage()
        result = storage.update_blob("test-blob.jpg", {"key": "value"})

        # Verify result is False when update fails
        self.assertFalse(result)

    @patch.dict(
        os.environ,
        {
            "AZURE_STORAGE_CONNECTION_STRING": "test_connection_string",
            "AZURE_DEFAULT_CONTAINER": "custom-default",
        },
    )
    @patch("utils.blob_storage.BlobServiceClient")
    def test_custom_default_container(self, mock_blob_service_client):
        # Test initialization with custom default container from environment
        storage = AzureBlobStorage()

        # Verify custom default container is set correctly
        self.assertEqual(storage.default_container, "custom-default")
