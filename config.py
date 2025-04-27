import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment
mongo_uri = os.getenv("MONGO_URI")

# Initialize MongoDB client
mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1')) 