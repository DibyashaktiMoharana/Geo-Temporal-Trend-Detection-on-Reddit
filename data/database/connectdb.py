import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connectdb():
    """Connect to MongoDB using MONGO_URI from environment variables"""
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable is not set")
    
    try:
        # Create a new client and connect to the server
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

def get_collection(collection_name: str):
    """Get a collection from the database"""
    client = connectdb()
    db = client.reddit_data  # Database name
    return db[collection_name]
