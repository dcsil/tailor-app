import base64
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
import cohere
from init_mongo import insert_document, find_documents, delete_document, update_document
from utils.helpers import ALLOWED_EXTENSIONS, allowed_file
from utils.blob_storage import blob_storage

co = cohere.ClientV2()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
file_bp = Blueprint("file_bp", __name__)


# Define valid file classes
VALID_CLASSES = {
    "art and film",
    "fabric",
    "fashion illustration",
    "garment",
    "historical photograph",
    "location photograph",
    "nature",
    "runway",
    "street style photograph",
    "texture",
}


@file_bp.route("/api/files/analyze", methods=["POST"])
def analyze_file():
    """
    Endpoint to analyze an uploaded image using Cohere AI.

    Request:
    - file: The image file to analyze.

    Response:
    - success (bool): Whether the request was processed successfully.
    - analysis (str): A JSON string containing:
        - A brief description of the image's vibe.
        - The classification from a predefined list.
        - The main colors present in the image.
    """
    try:
        # Check if file is included
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        # Convert image to base64 for Cohere API
        image_base64 = base64.b64encode(file.read()).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64}"
        # Construct the AI prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Can you return your answer as a list, with square brackets and quotations but without the indenting and formatting:",
                    },
                    {
                        "type": "text",
                        "text": "1. The general vibe in a brief sentence.",
                    },
                    {
                        "type": "text",
                        "text": "2. The classification from this list: ('fabric', 'fashion illustration', 'garment', 'historical photograph', 'location photograph', 'nature', 'runway', 'street style photograph', 'texture').",
                    },
                    {
                        "type": "text",
                        "text": "3. The main colors in the image, separated by commas.",
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        # Call Cohere AI
        response = co.chat(model="c4ai-aya-vision-8b", messages=messages, temperature=0)
        # Extract response
        return (
            jsonify({"success": True, "analysis": response.message.content[0].text}),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@file_bp.route("/api/files/upload", methods=["POST"])
def upload_file():
    """
    Endpoint to upload a file to Azure Blob Storage and store metadata in MongoDB

    Request requires:
    - file: The file to upload
    - description: Text description of the file
    - user_id: ID of the user uploading the file
    - class: Classification of the file (from predefined list)
    - colour: Colour description of the file
    """
    try:
        # Check if all required fields are present
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        # Check if the file is empty
        if not file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Check for valid file type
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                    }
                ),
                400,
            )

        # Get other form data
        description = request.form.get("description", "")
        user_id = request.form.get("user_id")
        file_class = request.form.get("class", "")
        colour = request.form.get("colour", "")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Validate class if provided
        if file_class and file_class not in VALID_CLASSES:
            return (
                jsonify(
                    {
                        "error": f"Invalid class. Allowed classes: {', '.join(VALID_CLASSES)}"
                    }
                ),
                400,
            )

        # Secure the filename
        secure_name = secure_filename(file.filename)

        # Upload to Azure Blob Storage
        upload_result = blob_storage.upload_file(
            file_data=file.read(), original_filename=secure_name
        )

        embedding = co.embed(
            texts=[description, file_class, colour],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        ).embeddings.float

        # Prepare document for MongoDB
        file_document = {
            "filename": secure_name,
            "blob_name": upload_result["blob_name"],
            "blob_url": upload_result["blob_url"],
            "description": description,
            "size_bytes": upload_result["size"],
            "timestamp": datetime.utcnow(),
            "container": upload_result["container"],
            "embedding": embedding[0],
            "class": file_class,
            "colour": colour,
        }

        # Store metadata in MongoDB
        document_id = insert_document(user_id, "files", file_document)

        # Add the MongoDB ID to the response
        upload_result["document_id"] = document_id
        upload_result["original_filename"] = secure_name
        upload_result["description"] = description
        upload_result["class"] = file_class
        upload_result["colour"] = colour

        return (
            jsonify(
                {
                    "success": True,
                    "message": "File uploaded successfully",
                    "file_data": upload_result,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in file upload: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@file_bp.route("/api/files/user/<user_id>", methods=["GET"])
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
            file_doc["_id"] = str(file_doc["_id"])
            # Convert datetime objects to ISO format strings
            if "timestamp" in file_doc:
                file_doc["timestamp"] = file_doc["timestamp"].isoformat()
            files_list.append(file_doc)

        return (
            jsonify({"success": True, "count": len(files_list), "files": files_list}),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving user files: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@file_bp.route("/api/files/<user_id>/<file_id>", methods=["DELETE"])
def delete_file(user_id, file_id):
    """
    Endpoint to delete a file (both from Azure Blob Storage and MongoDB)
    """
    try:
        # Find the file document first to get the blob name
        file_docs = list(find_documents(user_id, "files", {"_id": ObjectId(file_id)}))

        if not file_docs:
            return jsonify({"error": "File not found"}), 404

        file_doc = file_docs[0]
        blob_name = file_doc.get("blob_name")
        container = file_doc.get("container")

        # Delete from Azure Blob Storage
        if blob_name:
            blob_deleted = blob_storage.delete_blob(blob_name, container)
            if not blob_deleted:
                logger.warning(
                    f"Could not delete blob {blob_name} from container {container}"
                )

        # Delete from MongoDB
        delete_document(user_id, "files", file_id)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "File deleted successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@file_bp.route("/api/files/<user_id>/<file_id>", methods=["PATCH"])
def update_file(user_id, file_id):
    """
    Endpoint to update file metadata (description, class, colour) in MongoDB and Azure Blob Storage
    """
    try:
        # Find the file document first
        file_docs = list(find_documents(user_id, "files", {"_id": ObjectId(file_id)}))

        if not file_docs:
            return jsonify({"error": "File not found"}), 404

        file_doc = file_docs[0]
        blob_name = file_doc.get("blob_name")
        container = file_doc.get("container")

        # Get updated fields
        description = request.form.get("description", file_doc.get("description", ""))
        file_class = request.form.get("class", file_doc.get("class", ""))
        colour = request.form.get("colour", file_doc.get("colour", ""))

        # Validate class if it's been changed
        if (
            file_class
            and file_class != file_doc.get("class", "")
            and file_class not in VALID_CLASSES
        ):
            return (
                jsonify(
                    {
                        "error": f"Invalid class. Allowed classes: {', '.join(VALID_CLASSES)}"
                    }
                ),
                400,
            )

        # Update document fields
        file_doc["description"] = description
        file_doc["class"] = file_class
        file_doc["colour"] = colour

        # Update embedding
        new_embedding = co.embed(
            texts=[description, file_class, colour],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        ).embeddings.float
        file_doc["embedding"] = new_embedding[0]

        # Update in Azure Blob Storage
        if blob_name:
            blob_updated = blob_storage.update_blob(blob_name, file_doc, container)
            if not blob_updated:
                logger.warning(
                    f"Could not update blob {blob_name} in container {container}"
                )

        # Update in MongoDB
        result = update_document(user_id, "files", file_id, file_doc)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "File updated successfully",
                    "file_data": result,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error updating file: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@file_bp.route("/api/files/<user_id>/<file_id>", methods=["GET"])
def get_file_metadata(user_id, file_id):
    """
    Endpoint to retrieve file metadata (description, class, colour) of file_id from MongoDB.
    """
    try:
        # Find the file document
        file_docs = list(find_documents(user_id, "files", {"_id": ObjectId(file_id)}))

        if not file_docs:
            return jsonify({"error": "File not found"}), 404

        file_doc = file_docs[0]

        # Prepare metadata to return
        result = {
            "_id": str(file_doc["_id"]),
            "blob_name": file_doc.get("blob_name"),
            "description": file_doc.get("description", ""),
            "class": file_doc.get("class", ""),
            "colour": file_doc.get("colour", ""),
        }

        return jsonify({"success": True, "file_data": result}), 200

    except Exception as e:
        logger.error(f"Error retrieving file metadata: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
