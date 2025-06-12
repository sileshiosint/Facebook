import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "facebook_data")
POSTS_COLLECTION = os.getenv("POSTS_COLLECTION", "posts")

# Paths to keyword files
# Ensure the 'keywords' directory is correctly located relative to where analyzer.py will be run
# If analyzer.py is run from within nlp_analysis_engine directory:
KEYWORDS_DIR = "keywords"
# If analyzer.py is run from the root project directory:
# KEYWORDS_DIR = os.path.join("nlp_analysis_engine", "keywords")


HATE_SPEECH_KEYWORDS_FILE_EN = os.path.join(KEYWORDS_DIR, "hate_speech_en.txt")
EXTREMISM_KEYWORDS_FILE_EN = os.path.join(KEYWORDS_DIR, "extremism_en.txt")

# Optional: Translation API Key
# TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")
