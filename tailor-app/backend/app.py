import sentry_sdk
from flask import Flask, json, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import os.path
from pathlib import Path
from routes.pin_routes import insert_pins, pin_bp
from routes.chat_routes import chat_bp
from routes.moodboard_routes import moodboard_bp


# Import MongoDB functionality
from init_mongo import (
    initialize_mongo,
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

# Initialize MongoDB connection
mongo_client, mongo_db = initialize_mongo()

app.register_blueprint(pin_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(moodboard_bp)

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
    # Ensure database connection is initialized when running as a standalone app
    if mongo_client is None and mongo_db is None:
        initialize_mongo(force_connect=True)
    
    json_file_path = "./assets/sample_images.json"  # Adjust path if needed
    with open(json_file_path, "r") as file:
        post_data = json.load(file)
    
    # prepopulate the database with the sample data under ./assets/sample_images.json
    with app.test_request_context(method="POST", json=post_data):
        insert_pins()  
    
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)