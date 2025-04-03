from datetime import datetime
import logging
import cohere
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from init_mongo import insert_document, find_documents, delete_document
from utils.blob_storage import blob_storage
from utils.helpers import ALLOWED_EXTENSIONS, allowed_file

co = cohere.ClientV2()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
board_bp = Blueprint("board_bp", __name__)


@board_bp.route("/api/boards/upload", methods=["POST"])
def insert_moodboard():
    """
    Endpoint to insert (export) a moodboard to Azure Blob Storage and store metadata in MongoDB

    Request requires:
    - image_ids: The id of images on the moodboard
    - user_id: ID of the user uploading the board
    """
    try:
        # Check if all required fields are present
        if "file" not in request.files:
            return jsonify({"error": "No board provided"}), 400

        board = request.files["file"]

        # Check if the board is empty
        if not board.filename:
            return jsonify({"error": "No selected board"}), 400

        # Check for valid board type
        if not allowed_file(board.filename):
            return (
                jsonify(
                    {
                        "error": f"Board type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                    }
                ),
                400,
            )

        # Get other form data
        user_id = request.form.get("user_id")
        image_ids = request.form.get("image_ids")
        prompt = request.form.get("prompt")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Secure the filename
        secure_name = secure_filename(board.filename)

        # Upload to Azure Blob Storage
        upload_result = blob_storage.upload_file(
            file_data=board.read(), original_filename=secure_name
        )

        # Prepare document for MongoDB
        board_document = {
            "boardname": secure_name,
            "blob_name": upload_result["blob_name"],
            "blob_url": upload_result["blob_url"],
            "size_bytes": upload_result["size"],
            "timestamp": datetime.utcnow(),
            "container": upload_result["container"],
            "image_ids": image_ids,
            "prompt": prompt,
        }

        # Store metadata in MongoDB
        document_id = insert_document(user_id, "boards", board_document)

        # Add the MongoDB ID to the response
        upload_result["document_id"] = document_id
        upload_result["original_boardname"] = secure_name

        # delete the temporary board
        temp_board = list(find_documents(user_id, "temp_boards", {"prompt": prompt}))[0]
        delete_document(user_id, "temp_boards", str(temp_board["_id"]))

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Board exported successfully",
                    "board_data": upload_result,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in board upload: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@board_bp.route("/api/boards/user/<user_id>", methods=["GET"])
def get_moodboards(user_id):
    """
    Endpoint to retrieve all moodboards exported by a specific user
    """
    try:
        boards_cursor = find_documents(user_id, "boards", {})

        boards_list = []
        for board_doc in boards_cursor:
            # Convert ObjectId to string for JSON serialization
            board_doc["_id"] = str(board_doc["_id"])
            # Convert datetime objects to ISO format strings
            if "timestamp" in board_doc:
                board_doc["timestamp"] = board_doc["timestamp"].isoformat()
            boards_list.append(board_doc)

        return (
            jsonify(
                {"success": True, "count": len(boards_list), "boards": boards_list}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving user boards: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@board_bp.route("/api/boards/<user_id>/<board_id>", methods=["DELETE"])
def delete_moodboard(user_id, board_id):
    """
    Endpoint to delete a board (both from Azure Blob Storage and MongoDB)
    """
    try:
        # Find the board document first to get the blob name
        board_docs = list(
            find_documents(user_id, "boards", {"_id": ObjectId(board_id)})
        )

        if not board_docs:
            return jsonify({"error": "Board not found"}), 404

        board_doc = board_docs[0]
        blob_name = board_doc.get("blob_name")
        container = board_doc.get("container")

        # Delete from Azure Blob Storage
        if blob_name:
            blob_deleted = blob_storage.delete_blob(blob_name, container)
            if not blob_deleted:
                logger.warning(
                    f"Could not delete blob {blob_name} from container {container}"
                )

        # Delete from MongoDB
        delete_document(user_id, "boards", board_id)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Board deleted successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error deleting bord: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@board_bp.route("/api/temp_boards/<user_id>/<prompt>", methods=["DELETE"])
def delete_temp_moodboard(user_id, prompt):
    """
    Endpoint to delete a temporary board (from MongoDB)
    """
    try:
        # Find the board document first to get the blob name
        temp_boards = list(find_documents(user_id, "temp_boards", {"prompt": prompt}))
        if not temp_boards:
            return jsonify({"message": "No temp boards to delete."})

        temp_board = temp_boards[0]
        if not temp_board:
            return jsonify({"error": "Board not found"}), 404

        delete_document(user_id, "temp_boards", str(temp_board["_id"]))

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Temp board deleted successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error deleting temp bord: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
