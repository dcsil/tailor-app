import time
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

# Global variables
client = None
db = None
testing_mode = os.getenv("TESTING", "False").lower() == "true"

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

# Initialize MongoDB connection
def initialize_mongo(force_connect=False):
    global client, db
    
    if testing_mode and not force_connect:
        logger.info("Running in test mode without MongoDB connection")
        return None, None
    
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
        if force_connect:
            raise
        else:
            # Allow tests to continue
            logger.warning("Continuing without database connection for testing")
            return None, None

    db = client.get_database(DB_NAME)
    return client, db

# User collection management
def get_user_collection(user_id, collection_type):
    if db is None:
        if testing_mode:
            logger.debug(f"Test mode: Simulating access to collection user_{user_id}_{collection_type}")
            return MockCollection(f"user_{user_id}_{collection_type}")
        else:
            # Initialize connection for lazy loading
            initialize_mongo()
            if db is None:
                raise RuntimeError("Database connection failed and not in testing mode")
    
    existing_collections = db.list_collection_names()
    collection_name = f"user_{user_id}_{collection_type}"
    collection = db.get_collection(collection_name)
    if collection_type == "pins" and collection_name not in existing_collections:
        collection = db.create_collection(collection_name)
        collection.create_search_index({"definition":
            {"mappings":
                {"dynamic": True,
                "fields": {
                    "embedding" : {
                        "dimensions": 1024,
                        "similarity": "cosine",
                        "type": "knnVector"
                    },
                    "fullplot": {
                        "type": "string"
                    }
                    }}},
            "name": "default"
            }
        )
        logger.info("Waiting for the search index to get ready...")
        time.sleep(20) 
        
    return collection

# Basic CRUD operations
def insert_document(user_id, collection_type, document):
    collection = get_user_collection(user_id, collection_type)
    result = collection.insert_one(document)
    return str(result.inserted_id)

def insert_documents(user_id, collection_type, documents):
    collection = get_user_collection(user_id, collection_type)
    results = collection.insert_many(documents)
    return [str(doc_id) for doc_id in results.inserted_ids] 

def find_documents(user_id, collection_type, query=None):
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

def delete_documents(user_id, collection_type, document_ids):
    collection = get_user_collection(user_id, collection_type)
    object_ids = [ObjectId(doc_id) for doc_id in document_ids]  
    return collection.delete_many({"_id": {"$in": object_ids}})

# Stub for future vector operations
def vector_search_stub(user_id, query_text, limit=10):
    logger.info(f"Vector search stub called for user {user_id} with query: {query_text}")
    return []

# Initialize collections 
def initialize_user(user_id):
    # Conversations collection
    conversations = get_user_collection(user_id, "conversations")
    
    if not testing_mode:
        conversations.create_index("timestamp")
    
    logger.info(f"Initialized collections for user: {user_id}")
    
    return {
        "user_id": user_id,
        "initialized": True,
        "collections": ["conversations"]
    }

# Mock collection for testing
class MockCollection:
    def __init__(self, name):
        self.name = name
        self.data = []
        
    def insert_one(self, document):
        document_id = ObjectId()
        document["_id"] = document_id
        self.data.append(document)
        
        class Result:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return Result(document_id)
    
    def find(self, query=None):
        return []
    
    def update_one(self, filter_dict, update_dict):
        class Result:
            def __init__(self):
                self.modified_count = 0
        
        return Result()
    
    def delete_one(self, filter_dict):
        class Result:
            def __init__(self):
                self.deleted_count = 0
        
        return Result()
    
    def create_index(self, field_name):
        pass

# Only initialize connection if this file is run directly or if we're not in testing mode
if __name__ == "__main__" or not testing_mode:
    initialize_mongo()