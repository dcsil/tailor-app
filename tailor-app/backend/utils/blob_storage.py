from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
root_env = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=root_env, override=True)

class AzureBlobStorage:
    def __init__(self):
        # Connection string
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not self.connection_string:
            logger.error("AZURE_STORAGE_CONNECTION_STRING not set in environment variables")
            raise ValueError("Azure Storage connection string not configured")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        
        # Default container for user uploads
        self.default_container = os.getenv('AZURE_DEFAULT_CONTAINER', 'user-uploads')
    
    def get_container_client(self, container_name=None):
        """
        Get a container client for the specified container or the default one
        """
        container = container_name or self.default_container
        return self.blob_service_client.get_container_client(container)
    
    def upload_file(self, file_data, original_filename, container_name=None):
        """
        Upload a file to Azure Blob Storage
        
        Args:
            file_data: The file data (e.g., from request.files)
            original_filename: Original filename
            container_name: Optional container name, uses default if not specified
            
        Returns:
            Dict with blob_url, blob_name
        """
        try:
            container_client = self.get_container_client(container_name)
            
            # Generate a unique blob name to avoid collisions
            # Using UUID and keeping the original extension
            file_extension = Path(original_filename).suffix
            blob_name = f"{uuid.uuid4()}{file_extension}"
            
            # Upload the file
            blob_client = container_client.upload_blob(
                name=blob_name,
                data=file_data,
                overwrite=True
            )
            
            # Generate the URL for the uploaded blob
            blob_url = f"{container_client.url}/{blob_name}"
            
            logger.info(f"File uploaded successfully: {blob_url}")
            
            return {
                "blob_name": blob_name,
                "blob_url": blob_url,
                "container": container_client.container_name,
                "size": len(file_data)
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to Azure Blob Storage: {e}")
            raise
    
    def delete_blob(self, blob_name, container_name=None):
        """
        Delete a blob from Azure Blob Storage
        """
        try:
            container_client = self.get_container_client(container_name)
            container_client.delete_blob(blob_name)
            logger.info(f"Blob '{blob_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting blob from Azure Blob Storage: {e}")
            return False
    
    def update_blob(self, blob_name, new_file_data, container_name=None):
        """
        Update a blob in Azure Blob Storage
        """
        try:
            container_client = self.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(new_file_data, overwrite=True)
            logger.info(f"Blob '{blob_name}' updates successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting blob from Azure Blob Storage: {e}")
            return False
        
# Create a singleton instance
blob_storage = AzureBlobStorage()