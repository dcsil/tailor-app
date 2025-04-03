import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

# connection string
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# container client, either one of the following:
### pinterest-images
### user-uploads
container_name = "user-uploads"
container_client = blob_service_client.get_container_client(container_name)

# upload file to container
blob_name = "frankenpet.png"
blob_path = "/Users/nina/Desktop/frankenpet.png"
with open(blob_path, "rb") as data:
    container_client.upload_blob(name=blob_name, data=data)
