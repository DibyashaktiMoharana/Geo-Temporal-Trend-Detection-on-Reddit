import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Constants
DATABASE_NAME = "reddit_data"
COLLECTION_SUFFIX = "Data"

# Singleton client instance
_client_instance: Optional[MongoClient] = None

def get_db_client():
    """
    Get MongoDB client instance (singleton pattern)
    Reuses existing connection if available
    """
    global _client_instance
    
    if _client_instance is None:
        mongo_uri = os.getenv("MONGO_URI")
        
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable is not set")
        
        try:
            _client_instance = MongoClient(mongo_uri, server_api=ServerApi('1'))
            # Verify connection
            _client_instance.admin.command('ping')
            print(f"✓ Successfully connected to MongoDB (Database: {DATABASE_NAME})")
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise
    
    return _client_instance

def get_database():
    """Get the reddit_data database"""
    client = get_db_client()
    return client[DATABASE_NAME]

def get_collection(collection_name: str):
    """
    Get a collection from the database
    
    Args:
        collection_name: Name of the collection (e.g., 'delhiData', 'puneData')
    
    Returns:
        MongoDB collection object
    """
    db = get_database()
    return db[collection_name]

def get_collection_for_subreddit(subreddit_name: str):
    """
    Get collection name for a subreddit
    Converts subreddit name to collection name format (e.g., 'delhi' -> 'delhiData')
    
    Args:
        subreddit_name: Name of the subreddit
    
    Returns:
        Collection name
    """
    collection_name = f"{subreddit_name.lower()}{COLLECTION_SUFFIX}"
    return get_collection(collection_name)

def list_all_collections():
    """List all collection names in the database"""
    db = get_database()
    return db.list_collection_names()

def get_all_subreddit_collections():
    """
    Get all collections that end with 'Data' (subreddit collections)
    
    Returns:
        List of collection names
    """
    collections = list_all_collections()
    return [col for col in collections if col.endswith(COLLECTION_SUFFIX)]

def close_connection():
    """Close MongoDB connection"""
    global _client_instance
    if _client_instance:
        _client_instance.close()
        _client_instance = None
        print("✓ MongoDB connection closed")
