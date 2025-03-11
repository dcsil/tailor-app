from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
backend_env = BASE_DIR / ".env"
root_env = BASE_DIR.parent / ".env"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=root_env, override=True)

# Configuration management with validation
def get_config():
    config = {
        "mongo_uri": os.getenv("MONGO_URI"),
        "db_name": os.getenv("DB_NAME")
    }

    # Set defaults if not provided
    if not config["mongo_uri"]:
        logger.warning("MONGO_URI not set, using default localhost connection")
        config["mongo_uri"] = "mongodb://localhost:27017"
    
    if not config["db_name"]:
        logger.warning("DB_NAME not set, using default 'app_mvp'")
        config["db_name"] = "app_mvp"
    
    # Validate critical configurations
    if config["mongo_uri"].startswith("mongodb+srv://") and ":" not in config["mongo_uri"]:
        logger.error("Invalid MONGO_URI format: MongoDB Atlas connection string should include credentials")
        sys.exit(1)
    
    logger.info(f"Using database: {config['db_name']}")
    return config

# Get validated configuration
config = get_config()
MONGO_URI = config["mongo_uri"]
DB_NAME = config["db_name"]

# Connection with timeout settings for cloud deployment
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,  # 5 seconds timeout for server selection
    connectTimeoutMS=10000,         # 10 seconds to establish a connection
    socketTimeoutMS=45000           # 45 seconds for operations
)

try:
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB Atlas")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB Atlas: {e}")
    raise

db = client.get_database(DB_NAME)


# User collection management
def get_user_collection(user_id, collection_type):
    return db.get_collection(f"user_{user_id}_{collection_type}")

# Basic CRUD operations
def insert_document(user_id, collection_type, document):
    collection = get_user_collection(user_id, collection_type)
    result = collection.insert_one(document)
    return str(result.inserted_id)

def find_documents(user_id, collection_type, query = None):
    collection = get_user_collection(user_id, collection_type)
    return collection.find(query or {})

def update_document(user_id, collection_type, document_id, update):
    collection = get_user_collection(user_id, collection_type)
    return collection.update_one(
        {"_id": ObjectId(document_id)}, 
        {"$set": update}
    )

def delete_document(user_id, collection_type, document_id):
    collection = get_user_collection(user_id, collection_type)
    return collection.delete_one({"_id": ObjectId(document_id)})

# Stub for future vector operations
def vector_search_stub(user_id, query_text, limit = 10):
    logger.info(f"Vector search stub called for user {user_id} with query: {query_text}")
    return []

# Initialize collections 
def initialize_user(user_id):
    # Conversations collection
    conversations = get_user_collection(user_id, "conversations")
    conversations.create_index("timestamp")
    
    logger.info(f"Initialized collections for user: {user_id}")
    
    return {
        "user_id": user_id,
        "initialized": True,
        "collections": ["conversations"]
    }