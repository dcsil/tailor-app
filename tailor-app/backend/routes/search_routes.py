import logging
from flask import Blueprint, jsonify, request
from utils.helpers import get_user_id
from usecases.text_prompt import search_database
from init_mongo import (
    find_documents,
    get_user_collection,
    insert_document,
    update_document,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_bp = Blueprint("moodboard", __name__)
generated_images = set()  # Keep track of already generated images


@search_bp.route("/api/search-prompt", methods=["POST"])
def search_prompt():
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' field in request"}), 400

    try:
        user_id = get_user_id()
        files_collection = get_user_collection(user_id, "files")
        image_ids, blob_urls = search_database(
            files_collection, prompt, postfilter={"score": {"$gt": 0}}
        )
        temp_board_document = {
            "prompt": prompt,
            "curr_images": [
                [image_ids[i], blob_urls[i]] for i in range(len(image_ids))
            ],  # The images that have already been generated on the board
            "queue_images": [],  # Queue to store generated images
        }

        # Store temp board metadata in MongoDB to keep track of the current image ids (that are subject to change)
        insert_document(user_id, "temp_boards", temp_board_document)

        return jsonify(
            {"image_ids": image_ids, "blob_urls": blob_urls, "user_id": user_id}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@search_bp.route("/api/regenerate-search", methods=["POST"])
def regenerate_search():
    """
    The images are regenerated in batch and stored in the queue. This is more efficient than calling the endpoint every single time
    that regenerate button is clicked.
    """
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' field in request"}), 400

    try:
        user_id = get_user_id()
        files_collection = get_user_collection(user_id, "files")
        temp_board = list(find_documents(user_id, "temp_boards", {"prompt": prompt}))[0]
        temp_board_id = temp_board["_id"]
        queue_images = temp_board["queue_images"]
        curr_images = temp_board["curr_images"]

        if not queue_images:
            # Have the database NOT search among the already generated image ids
            image_ids, blob_urls = search_database(
                files_collection,
                prompt,
                postfilter={"score": {"$gt": 0}},
                excluded_ids=[img[0] for img in curr_images],
            )

            if not image_ids:
                return jsonify(
                    {
                        "image_ids": image_ids,
                        "blob_urls": blob_urls,
                        "success": "No new relevant images found",
                    }
                )

            # Add new unique images to queue
            for i in range(min(len(image_ids), 10)):
                queue_images.append([image_ids[i], blob_urls[i]])

        next_image_id, next_image_url = queue_images.pop(0)
        curr_images.append([next_image_id, next_image_url])
        temp_board["queue_images"] = queue_images
        temp_board["curr_images"] = curr_images
        update_document(user_id, "temp_boards", temp_board_id, temp_board)

        return jsonify(
            {
                "next_image": [next_image_id, next_image_url],
                "remaining_queue_size": len(queue_images),
                "user_id": user_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
