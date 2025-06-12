import time
import random
from pymongo import MongoClient
# Ensure that config is imported correctly based on your project structure.
# If utils.py and config.py are in the same directory (facebook_scraper),
# and you run scripts from the parent directory of facebook_scraper,
# or if facebook_scraper is a package, then .config should work.
# If you run scripts directly from the facebook_scraper directory,
# you might need to adjust the import to `import config`
# or handle sys.path modifications.
from .config import MONGO_URI, DB_NAME

def random_delay(min_seconds=1, max_seconds=5):
    """Waits for a random duration between min_seconds and max_seconds."""
    delay = random.uniform(min_seconds, max_seconds)
    # print(f"Utils: Applying random delay of {delay:.2f} seconds.") # Optional: for debugging
    time.sleep(delay)

def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # You might want to add a check here to confirm the connection
        # For example, by listing collections or checking server status
        # Attempt to get server info to confirm connection
        client.server_info()
        print(f"Successfully connected to MongoDB: {DB_NAME} at {MONGO_URI}")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
