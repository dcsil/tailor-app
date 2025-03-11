import sentry_sdk
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import cohere
import os
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import os.path
import uuid
from pathlib import Path

# Import MongoDB functionality
from init_mongo import (
    initialize_user,
    insert_document,
    find_documents,
    update_document
)

sentry_sdk.init(
    dsn="https://31ac1b5e4bbf822e2c0589df00b27a26@o4508887891836928.ingest.us.sentry.io/4508905308815360",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

BASE_DIR = Path(__file__).resolve().parent
backend_env = BASE_DIR / ".env"
root_env = BASE_DIR.parent / ".env"

# Load environment variables
load_dotenv(dotenv_path=root_env, override=True)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/dist')
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
CORS(app)  # Enable CORS for development

# Initialize Cohere client
co = cohere.ClientV2(
    api_key=os.getenv('COHERE_API_KEY'))
CHAT_MODEL = "command-r-08-2024"

# Prompt templates
TEMPLATES = {
    'basic_chat': {
        'system_prompt': "You are a helpful fashion assistant.",
        'temperature': 0.7,
        'max_tokens': 300
    },
    'expert_mode': {
        'system_prompt': "You are an expert programmer focused on providing technical solutions.",
        'temperature': 0.3,
        'max_tokens': 500
    }
}
  
# For demo purposes - enables session user tracking
def get_user_id():
    """Get current user ID from session or create a temporary one"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
        # Initialize collections for this user
        initialize_user(session['user_id'])
        print(f"Created new user ID: {session['user_id']}")
    return session['user_id']

@app.route('/api/generate', methods=['POST'])
def generate_response():
    data = request.json
    user_prompt = data.get('prompt', '')
    template_name = data.get('template', 'basic_chat')
    
    try:
        template = TEMPLATES[template_name]
        user_id = get_user_id()
        
        # Store conversation in MongoDB
        conversation_doc = {
            "prompt": user_prompt,
            "template": template_name,
            "timestamp": time.time()
        }
        
        doc_id = insert_document(user_id, "conversations", conversation_doc)
        print(f"Saved conversation with ID: {doc_id}")

        response = co.chat(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": template['system_prompt']},
                {"role": "user", "content": user_prompt}
            ],
            temperature=template['temperature'],
            max_tokens=template['max_tokens']
        )
        
        response_text = response.message.content[0].text
        
        # Update the document with the response
        update_document(
            user_id, 
            "conversations", 
            doc_id, 
            {"response": response_text}
        )
        
        return jsonify({
            'response': response_text,
            'conversation_id': doc_id,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retrieve conversation history for the current user"""
    user_id = get_user_id()
    
    # Fetch recent conversations
    conversations = list(find_documents(
        user_id, 
        "conversations", 
        {}
    ).sort("timestamp", -1).limit(10))
    
    # Convert ObjectId to string for JSON serialization
    for conv in conversations:
        conv["_id"] = str(conv["_id"])
    
    return jsonify(conversations)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route("/error/test")
def error_test():
    1/0  # raises an error
    return "<p>This is a Sentry error test.</p>"

# Serve static files from the React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
