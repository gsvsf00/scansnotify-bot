# mongodb_connection.py
import pymongo
from dotenv import load_dotenv
import os

class MongoDBConnectionError(Exception):
    pass

class MongoDBHandler:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Access MongoDB connection string
        mongo_url = os.getenv("MONGO_URL")

        # Access MongoDB database name and collection name
        db_name = os.getenv("MONGO_DB_NAME")
        collection_name = os.getenv("MONGO_COLLECTION_NAME")

        try:
            # Connect to MongoDB
            client = pymongo.MongoClient(mongo_url)

            # Access the specified database and collection
            db = client[db_name]
            collection = db[collection_name]

            # Print a message to the console if the connection is successful
            print("Connected to MongoDB!")

            # Set class attributes for client, db, and collection
            self.client = client
            self.db = db
            self.collection = collection

        except pymongo.errors.ConnectionFailure as e:
            # Raise a custom exception if the connection fails
            raise MongoDBConnectionError(f"Failed to connect to MongoDB. Error: {e}")

    def save_user_data(self, user_id, user_data):
        # Save or update user data in MongoDB based on user_id
        self.collection.update_one({"user_id": user_id}, {"$set": {"app": user_data}})

    def get_user_data(self, user_id):
        # Retrieve user data from MongoDB using the collection
        user_data = self.collection.find_one({"user_id": user_id})
        return user_data

    def create_user(self, user_id, username, first_name, last_name):
        # Create a new user in MongoDB
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "scans": []
        }
        self.collection.insert_one(user_data)

    def add_scan(self, user_id, name, source):
        # Add a new scan to the user's scans in MongoDB
        self.collection.update_one(
            {"user_id": user_id},
            {"$push": {"scans": {"name": name, "source": source}}}
        )

    def list_scans(self, user_id):
        # Retrieve user's scans from MongoDB
        user_data = self.collection.find_one({"user_id": user_id})
        if user_data and "scans" in user_data:
            return [f"{scan['name']} from {scan['source']}" for scan in user_data['scans']]
        else:
            return []
