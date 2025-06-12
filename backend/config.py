import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "facebook_data") # Default to facebook_data as used elsewhere
POSTS_COLLECTION = os.getenv("POSTS_COLLECTION", "posts")
PROFILES_COLLECTION = os.getenv("PROFILES_COLLECTION", "profiles")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users") # Added users collection

# For JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-please-change-in-prod") # Ensure a default is somewhat usable but emphasize change
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) # Made into int directly
