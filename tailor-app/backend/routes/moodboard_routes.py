from flask import Blueprint, jsonify, request
from utils.helpers import get_user_id
from usecases.text_prompt import search_database
from init_mongo import get_user_collection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

moodboard_bp = Blueprint('moodboard', __name__)

@moodboard_bp.route('/api/search-prompt', methods=['POST'])
def search_prompt():
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "Missing 'prompt' field in request"}), 400

    try:
        user_id = get_user_id()
        files_collection = get_user_collection(user_id, "files")
        image_ids = search_database(files_collection, prompt, postfilter={"score": {"$gt":0.3}})
        return jsonify({
            'image_ids': image_ids,
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    