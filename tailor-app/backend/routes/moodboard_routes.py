from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
import os
from datetime import datetime
import logging
from utils.blob_storage import blob_storage
from init_mongo import insert_document, find_documents, delete_document
from werkzeug.utils import secure_filename
from utils.helpers import allowed_file, ALLOWED_EXTENSIONS
import cohere
import base64
import json

co = cohere.ClientV2()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
board_bp = Blueprint('board_bp', __name__)

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB in bytes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@board_bp.route('/api/boards/analyze', methods=['POST'])
def analyze_moodboardV2():
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file format and size
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file format"}), 400

        if file.content_length > MAX_IMAGE_SIZE:
            return jsonify({"error": "File size exceeds 20 MB"}), 400

        # Convert image to base64
        image_base64 = base64.b64encode(file.read()).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64}"

        # Get image descriptions
        image_descriptions = request.form.get('image_descriptions', '[]')
        try:
            image_descriptions = json.loads(image_descriptions)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid image_descriptions format"}), 400

        # Validate image_descriptions
        if not isinstance(image_descriptions, list):
            return jsonify({"error": "image_descriptions must be a list"}), 400

        # Format descriptions into a string
        descriptions_text = "\n".join([
            f"Image {i+1}: {description}" 
            for i, description in enumerate(image_descriptions)
        ])

        # Construct the AI prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"The image I gave you is a moodboard consisting of multiple images. Here are the descriptions of the images:\n{descriptions_text}\nFollow these steps, considering both the moodboard and provided image descriptions:"
                    },
                    {
                        "type": "text",
                        "text": "1. First, provide the overall theme and mood of the moodboard."},
                    {
                        "type": "text",
                        "text": "2. Second, provide an in-depth analysis of the moodboard in a way that would be useful to a fashion designer. Include topics like textures, fabrics, colours, and anything else that would be important to a fashion designer."},
                    {
                        "type": "text",
                        "text": "3. Do not mention anything about a fashion designer. Do not mention the images themselves, such as 'Image 1'."},
                    {
                        "type": "text",
                        "text": "4. Use markdown to write your response in a very organized, easy-to-read format with headers and bold font where appropriate. The title must be related to the theme of the moodboard."},
                    
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ]

        # Call Cohere API
        response = co.chat(
            model="c4ai-aya-vision-8b",
            messages=messages,
            temperature=0
        )

        return jsonify({
            "success": True,
            "analysis": response.message.content[0].text
        }), 200

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@board_bp.route('/api/boards/nodescriptionsanalyze', methods=['POST'])
def analyze_moodboard():
    """
    Endpoint to analyze the current moodboard using Cohere AI.

    Request:
    - file: The image file to analyze.

    Response:
    - success (bool): Whether the request was processed successfully.
    - analysis (str): The analysis of the moodboard.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
    
        file = request.files['file']

        if not file:
            return jsonify({"error": "No file received"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file format"}), 400

        if file.content_length > MAX_IMAGE_SIZE:
            return jsonify({"error": "File size exceeds 20 MB"}), 400
    
        # Convert image to base64 for Cohere API
        image_base64 = base64.b64encode(file.read()).decode("utf-8")
        image_url = f"data:image/png;base64,{image_base64}"
        
        # Construct the AI prompt, Batch processing because Aya only accepts 4 images
        messages = [
            {"role": "user", "content": [
                {"type": "text", "text": "The image I gave you is a moodboard consisting of multiple images. Follow these steps:"},
                {"type": "text", "text": "1. Provide the overall mood of the moodboard."},
                {"type": "text", "text": "2. Provide an in-depth analysis of the moodboard in a way that would be useful to a fashion designer. Do not talk about the color palette. Do not say anything like 'a fashion designer's perspective'."},
                {"type": "text", "text": "3. Use markdown to write your response in a very organized, easy-to-read format with appropriate headers."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}
        ]

        response = co.chat(model="c4ai-aya-vision-8b", messages=messages, temperature=0)

        # Extract response
        return jsonify({
            "success": True,
            "analysis": response.message.content[0].text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# def analyze_moodboard_batch():
#     """
#     Endpoint to analyze the current moodboard using Cohere AI.

#     Request:
#     - files: The image file to analyze.

#     Response:
#     - success (bool): Whether the request was processed successfully.
#     - analysis (str): The analysis of the moodboard.
#     """
#     try:
#         # Check if file(s) are included
#         if 'files' not in request.files:
#             return jsonify({"error": "No files uploaded"}), 400
        
#         files = request.files.getlist('files')

#         if not files:
#             return jsonify({"error": "No files received"}), 400

#         image_urls = []
#         for file in files:
#             # Convert each image to Base64 URL format
#             image_data = file.read()
#             if not image_data:
#                 return jsonify({"error": "Empty file received"}), 400
            
            
#             image_base64 = base64.b64encode(image_data).decode("utf-8")
#             image_url = f"data:image/png;base64,{image_base64}"
#             image_urls.append(image_url)
        
#         # Construct the AI prompt, Batch processing because Aya only accepts 4 images
#         batch_size = 4
#         analyses = []

#         for i in range(0, len(image_urls), batch_size):
#             batch = image_urls[i:i + batch_size]
#             messages = [
#                 {"role": "user", 
#                  "content": [
#                      {"type": "text", "text": "Provide an in-depth analysis of these images in a way that would be useful to a fashion designer."},
#                      *[{"type": "image_url", "image_url": {"url": url}} for url in batch]
#                  ]
#                 }
#             ]

#             # Call Cohere AI Part 1
#             response = co.chat(model="c4ai-aya-vision-8b", messages=messages, temperature=0)
#             analyses.append(response.message.content[0].text)

#         # Call Cohere AI Part 2 (summarize the batches)
#         messages = [
#             {"role": "user", 
#                 "content": [
#                     {"type": "text", "text": "Combine these analyses into one analysis."},
#                     *[{"type": "text", "text": analysis} for analysis in analyses]
#                 ]
#             }
#         ]

#         response = co.chat(model="c4ai-aya-vision-8b", messages=messages, temperature=0)
#         final_analysis = response.message.content[0].text

#         # Extract response
#         return jsonify({
#             "success": True,
#             "analysis": final_analysis
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@board_bp.route('/api/boards/upload', methods=['POST'])
def insert_moodboard():

    """
    Endpoint to insert (export) a moodboard to Azure Blob Storage and store metadata in MongoDB
    
    Request requires:
    - image_ids: The id of images on the moodboard
    - user_id: ID of the user uploading the board
    """
    try:
        # Check if all required fields are present
        if 'file' not in request.files:
            return jsonify({"error": "No board provided"}), 400
        
        board = request.files['file']
        
        # Check if the board is empty
        if board.filename == '':
            return jsonify({"error": "No selected board"}), 400
        
        # Check for valid board type
        if not allowed_file(board.filename):
            return jsonify({"error": f"Board type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Get other form data
        user_id = request.form.get('user_id')
        image_ids = request.form.get('image_ids')
        prompt = request.form.get('prompt')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Secure the filename
        secure_name = secure_filename(board.filename)
        
        # Upload to Azure Blob Storage
        upload_result = blob_storage.upload_file(
            file_data=board.read(),
            original_filename=secure_name
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
        
        return jsonify({
            "success": True,
            "message": "Board exported successfully",
            "board_data": upload_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in board upload: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@board_bp.route('/api/boards/user/<user_id>', methods=['GET'])
def get_moodboards(user_id):
    """
    Endpoint to retrieve all moodboards exported by a specific user
    """
    try:
        boards_cursor = find_documents(user_id, "boards", {})
        
        boards_list = []
        for board_doc in boards_cursor:
            # Convert ObjectId to string for JSON serialization
            board_doc['_id'] = str(board_doc['_id'])
            # Convert datetime objects to ISO format strings
            if 'timestamp' in board_doc:
                board_doc['timestamp'] = board_doc['timestamp'].isoformat()
            boards_list.append(board_doc)
        
        return jsonify({
            "success": True,
            "count": len(boards_list),
            "boards": boards_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user boards: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@board_bp.route('/api/boards/<user_id>/<board_id>', methods=['DELETE'])
def delete_moodboard(user_id, board_id):
    """
    Endpoint to delete a board (both from Azure Blob Storage and MongoDB)
    """
    try:
        # Find the board document first to get the blob name
        board_docs = list(find_documents(user_id, "boards", {"_id": ObjectId(board_id)}))
        
        if not board_docs:
            return jsonify({"error": "Board not found"}), 404
            
        board_doc = board_docs[0]
        blob_name = board_doc.get("blob_name")
        container = board_doc.get("container")
        
        # Delete from Azure Blob Storage
        if blob_name:
            blob_deleted = blob_storage.delete_blob(blob_name, container)
            if not blob_deleted:
                logger.warning(f"Could not delete blob {blob_name} from container {container}")
        
        # Delete from MongoDB
        delete_document(user_id, "boards", board_id)
        
        return jsonify({
            "success": True,
            "message": "Board deleted successfully",
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting bord: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@board_bp.route('/api/temp_boards/<user_id>/<prompt>', methods=['DELETE'])
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

        return jsonify({
            "success": True,
            "message": "Temp board deleted successfully",
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting temp bord: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
