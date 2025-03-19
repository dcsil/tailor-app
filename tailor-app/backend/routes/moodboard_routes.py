from flask import Blueprint, json, jsonify, request
from utils.helpers import get_user_id
from routes.pin_routes import get_pins
from usecases.text_prompt import search_database
from init_mongo import get_user_collection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

moodboard_bp = Blueprint('moodboard', __name__)

@moodboard_bp.route('/api/search-prompt', methods=['POST'])
def search_prompt():
    prompt = request.json["prompt"]
    
    try:
        user_id = get_user_id()
        pin_collection = get_user_collection(user_id, "pins")
        response_data = get_pins().response[0].decode('utf-8')  
        response_json = json.loads(response_data)  
        pins = response_json.get("pins", [])
        image_ids = search_database(pin_collection, pins, prompt, postfilter={"score": {"$gt":0.3}})
        return jsonify({
            'image_ids': image_ids,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500