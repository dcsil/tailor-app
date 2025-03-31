from flask import Blueprint, request, jsonify
import time
from init_mongo import insert_document, update_document, find_documents
import cohere
import os
from utils.helpers import get_user_id

chat_bp = Blueprint('chat', __name__)

co = cohere.ClientV2(api_key=os.getenv('COHERE_API_KEY'))
CHAT_MODEL = "command-r-08-2024"

TEMPLATES = {
    'basic_chat': {'system_prompt': "You are a helpful fashion assistant.", 'temperature': 0.7, 'max_tokens': 300},
    'expert_mode': {'system_prompt': "You are an expert programmer focused on providing technical solutions.", 'temperature': 0.3, 'max_tokens': 500}
}


@chat_bp.route('/api/generate', methods=['POST'])
def generate_response():
    data = request.json
    user_prompt = data.get('prompt', '')
    template_name = data.get('template', 'basic_chat')

    try:
        template = TEMPLATES[template_name]
        user_id = get_user_id()
        
        conversation_doc = {"prompt": user_prompt, "template": template_name, "timestamp": time.time()}
        doc_id = insert_document(user_id, "conversations", conversation_doc)

        response = co.chat(
            model=CHAT_MODEL,
            messages=[{"role": "system", "content": template['system_prompt']}, {"role": "user", "content": user_prompt}],
            temperature=template['temperature'],
            max_tokens=template['max_tokens']
        )

        response_text = response.message.content[0].text
        update_document(user_id, "conversations", doc_id, {"response": response_text})

        return jsonify({'response': response_text, 'conversation_id': doc_id, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/api/history', methods=['GET'])
def get_history():
    try: 
        user_id = get_user_id()
        conversations = list(find_documents(user_id, "conversations", {}).sort("timestamp", -1).limit(10))
        for conv in conversations:
            conv["_id"] = str(conv["_id"])
        return jsonify(conversations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
