from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import logging
from utils.blob_storage import blob_storage
from init_mongo import insert_document, find_documents, delete_document
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
file_bp = Blueprint('file_bp', __name__)

# Define allowed file extensions for security
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route('/api/files/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to upload a file to Azure Blob Storage and store metadata in MongoDB
    
    Request requires:
    - file: The file to upload
    - description: Text description of the file
    - user_id: ID of the user uploading the file
    """
    try:
        # Check if all required fields are present
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Check if the file is empty
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Check for valid file type
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Get other form data
        description = request.form.get('description', '')
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Secure the filename
        secure_name = secure_filename(file.filename)
        
        # Upload to Azure Blob Storage
        upload_result = blob_storage.upload_file(
            file_data=file.read(),
            original_filename=secure_name
        )
        
        # Prepare document for MongoDB
        file_document = {
            "filename": secure_name,
            "blob_name": upload_result["blob_name"],
            "blob_url": upload_result["blob_url"],
            "description": description,
            "size_bytes": upload_result["size"],
            "timestamp": datetime.utcnow(),
            "container": upload_result["container"]
        }
        
        # Store metadata in MongoDB
        document_id = insert_document(user_id, "files", file_document)
        
        # Add the MongoDB ID to the response
        upload_result["document_id"] = document_id
        upload_result["original_filename"] = secure_name
        upload_result["description"] = description
        
        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "file_data": upload_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in file upload: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@file_bp.route('/api/files/user/<user_id>', methods=['GET'])
def get_user_files(user_id):
    """
    Endpoint to retrieve all files uploaded by a specific user
    """
    try:
        # Get all file documents for the user
        files_cursor = find_documents(user_id, "files", {})
        
        # Convert cursor to list for JSON serialization
        files_list = []
        for file_doc in files_cursor:
            # Convert ObjectId to string for JSON serialization
            file_doc['_id'] = str(file_doc['_id'])
            # Convert datetime objects to ISO format strings
            if 'timestamp' in file_doc:
                file_doc['timestamp'] = file_doc['timestamp'].isoformat()
            files_list.append(file_doc)
        
        return jsonify({
            "success": True,
            "count": len(files_list),
            "files": files_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user files: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@file_bp.route('/api/files/<user_id>/<file_id>', methods=['DELETE'])
def delete_file(user_id, file_id):
    """
    Endpoint to delete a file (both from Azure Blob Storage and MongoDB)
    """
    try:
        # Find the file document first to get the blob name
        file_docs = list(find_documents(user_id, "files", {"_id": file_id}))
        
        if not file_docs:
            return jsonify({"error": "File not found"}), 404
            
        file_doc = file_docs[0]
        blob_name = file_doc.get("blob_name")
        container = file_doc.get("container")
        
        # Delete from Azure Blob Storage
        if blob_name:
            blob_deleted = blob_storage.delete_blob(blob_name, container)
            if not blob_deleted:
                logger.warning(f"Could not delete blob {blob_name} from container {container}")
        
        # Delete from MongoDB
        result = delete_document(user_id, "files", file_id)
        
        return jsonify({
            "success": True,
            "message": "File deleted successfully",
            "delete_count": result.deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500