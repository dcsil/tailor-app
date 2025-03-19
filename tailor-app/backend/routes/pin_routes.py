from flask import Blueprint, request, jsonify
from bson import ObjectId
from init_mongo import insert_document, insert_documents, delete_document, delete_documents, update_document, find_documents
from utils.helpers import get_user_id
import cohere

co = cohere.ClientV2()
pin_bp = Blueprint('pins', __name__)

@pin_bp.route('/api/insert-pin', methods=['POST'])
def insert_pin():
    pin_data = request.json
    try:
        user_id = get_user_id() 
        pin_data["embedding"] = co.embed(
            texts=[pin_data["description"]],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        ).embeddings.float   
        
        pin_id = insert_document(user_id, "pins", pin_data)
        return jsonify({'pin_id': pin_id, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/insert-pins', methods=['POST'])
def insert_pins():
    pins_data = request.json
    try:
        user_id = get_user_id()    
        desc_emb = co.embed(
            texts=[p["description"] for p in pins_data],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        ).embeddings.float
        
        for i, _ in enumerate(pins_data):
            pins_data[i]["embedding"] = desc_emb[i]

        pin_ids = insert_documents(user_id, "pins", pins_data)
        return jsonify({'pin_ids': pin_ids, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/delete-pin', methods=['DELETE'])
def delete_pin():
    pin_id = request.json
    try:
        user_id = get_user_id()    
        delete_document(user_id, "pins", pin_id)
        return jsonify({'pin_id': pin_id, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/delete-pins', methods=['DELETE'])
def delete_pins():
    pin_ids = request.json
    try:
        user_id = get_user_id()    
        delete_documents(user_id, "pins", pin_ids)
        return jsonify({'pin_ids': pin_ids, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/update-pin', methods=['PATCH'])
def update_pin():
    pin_id = request.args.get('pin_id')
    pin_data = request.json
    try:
        user_id = get_user_id()    
        update_document(user_id, "pins", pin_id, pin_data) 
        return jsonify({'pin_id': pin_id, 'data': pin_data, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/get-pins', methods=['GET'])
def get_pins():
    user_id = get_user_id()
    pins = find_documents(user_id, "pins", {}) 
    sorted_pins = sorted(pins, key=lambda x: x.get("timestamp", 0), reverse=True)[:50]
    for pin in sorted_pins:
        pin["_id"] = str(pin["_id"])
    return jsonify({"pins": sorted_pins, "user_id": user_id})
