from flask import Blueprint, request, jsonify
from bson import ObjectId
from init_mongo import insert_document, insert_documents, delete_document, delete_documents, update_document, find_documents
from utils.helpers import get_user_id

pin_bp = Blueprint('pins', __name__)

@pin_bp.route('/api/insert-pin', methods=['POST'])
def insert_pin():
    pin_data = request.json
    try:
        user_id = get_user_id()    
        pin_id = insert_document(user_id, "pins", pin_data)
        return jsonify({'pin_id': str(pin_id), 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/insert-pins', methods=['POST'])
def insert_pins():
    pins_data = request.json
    try:
        user_id = get_user_id()    
        pin_ids = insert_documents(user_id, "pins", pins_data)
        return jsonify({'pin_ids': pin_ids, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/delete-pin', methods=['DELETE'])
def delete_pin():
    pin_id = request.json
    try:
        user_id = get_user_id()    
        delete_document(user_id, "pins", ObjectId(pin_id))
        return jsonify({'pin_id': pin_id, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/delete-pins', methods=['DELETE'])
def delete_pins():
    pin_ids = request.json
    try:
        user_id = get_user_id()    
        delete_documents(user_id, "pins", [ObjectId(pid) for pid in pin_ids])
        return jsonify({'pin_ids': pin_ids, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/update-pin', methods=['PATCH'])
def update_pin():
    pin_id = request.args.get('pin_id')
    pin_data = request.json
    try:
        user_id = get_user_id()    
        update_document(user_id, "pins", ObjectId(pin_id), pin_data) 
        return jsonify({'pin_id': pin_id, 'data': pin_data, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pin_bp.route('/api/get-pins', methods=['GET'])
def get_pins():
    user_id = get_user_id()
    pins = list(find_documents(user_id, "pins", {}).sort("timestamp", -1).limit(50))
    for pin in pins:
        pin["_id"] = str(pin["_id"])
    return jsonify({"pins": pins, "user_id": user_id})
