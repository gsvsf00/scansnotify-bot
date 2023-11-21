# mongodb_connection.py

import pymongo
from dotenv import load_dotenv
import os

def MongoDBHandler():
    # Load environment variables from .env file
    load_dotenv()

    # Access MongoDB connection string
    mongo_url = os.getenv("MONGO_URL")

    # Access MongoDB database name and collection name
    db_name = os.getenv("MONGO_DB_NAME")
    collection_name = os.getenv("MONGO_COLLECTION_NAME")

    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_url)

    # Access the specified database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Return the MongoDB client, database, and collection
    return client, db, collection
