from pymongo import MongoClient, errors as pymongo_errors # Import specific errors
from .config import MONGO_URI, DB_NAME
import sys # For exiting if DB connection fails at startup

client = None
db = None

def connect_to_mongo():
    global client, db
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) # Add timeout
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = client[DB_NAME]
        print("Backend: Successfully connected to MongoDB.")
    except pymongo_errors.ServerSelectionTimeoutError as err:
        print(f"Backend: MongoDB connection failed due to timeout: {err}")
        print(f"Backend: Check if MongoDB is running at {MONGO_URI} and accessible.")
        # Depending on policy, you might want the app to exit if DB is unavailable at startup
        # For now, it will allow app to start but get_db() will return None until connection succeeds
        # Consider exiting: sys.exit("MongoDB connection failed. Application cannot start.")
        client = None
        db = None
    except Exception as e:
        print(f"Backend: An unexpected error occurred during MongoDB connection: {e}")
        client = None
        db = None


def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Backend: MongoDB connection closed.")
        client = None
        db = None # Ensure db is also reset

def get_db():
    global db
    # Attempt to connect if db is None (e.g., initial call or after a failed connection)
    if db is None:
        print("Backend: DB instance is None, attempting to connect...")
        connect_to_mongo()

    # If client exists but db is somehow None (should not happen if connect_to_mongo is robust)
    # or if client is None (connection failed previously)
    if client is None and db is None: # Check if connection is still down
        print("Backend: MongoDB client not available. Trying to reconnect...")
        connect_to_mongo() # Attempt to reconnect
        if db is None: # If still None after reconnect attempt
             print("Backend: Failed to establish MongoDB connection after retry.")
             return None # Explicitly return None if connection is truly down
    return db
