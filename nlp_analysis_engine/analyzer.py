import os
from pymongo import MongoClient, UpdateOne
from langdetect import detect, LangDetectException
from datetime import datetime
import traceback # For more detailed error logging
import spacy # Import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # Import VADER

# Assuming config.py is in the same directory
from config import MONGO_URI, DB_NAME, POSTS_COLLECTION, \
                   HATE_SPEECH_KEYWORDS_FILE_EN, EXTREMISM_KEYWORDS_FILE_EN

# --- Global Variables / Initialization ---
NLP_MODEL_EN = None
SENTIMENT_ANALYZER = None

def initialize_nlp_models():
    """Loads NLP models: SpaCy for English and VADER Sentiment Analyzer."""
    global NLP_MODEL_EN, SENTIMENT_ANALYZER
    try:
        NLP_MODEL_EN = spacy.load("en_core_web_sm")
        print("NLP Engine: Successfully loaded SpaCy model 'en_core_web_sm'.")
    except OSError:
        print("NLP Engine: Error: SpaCy model 'en_core_web_sm' not found. ")
        print("Please run 'python -m spacy download en_core_web_sm' to download it.")
        NLP_MODEL_EN = None
    except Exception as e:
        print(f"NLP Engine: An unexpected error occurred while loading SpaCy model: {e}")
        NLP_MODEL_EN = None

    try:
        SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()
        print("NLP Engine: Successfully initialized VADER SentimentIntensityAnalyzer.")
    except Exception as e:
        print(f"NLP Engine: An unexpected error occurred while initializing VADER: {e}")
        SENTIMENT_ANALYZER = None


def get_db_connection(uri, db_name):
    """Establishes a connection to MongoDB and returns the database object."""
    try:
        client = MongoClient(uri)
        client.server_info() # Will raise an exception if connection failed
        db = client[db_name]
        print(f"NLP Engine: Successfully connected to MongoDB: {db_name} at {uri.split('@')[-1] if '@' in uri else uri}")
        return db
    except Exception as e:
        print(f"NLP Engine: Error connecting to MongoDB: {e}")
        print(traceback.format_exc())
        return None

def load_keywords(file_path):
    """Reads keywords from a given file path, returns a list of cleaned keywords."""
    keywords = []
    try:
        # Ensure the path is correct relative to the script's execution location
        # If analyzer.py is in nlp_analysis_engine, and keywords/ is also in nlp_analysis_engine
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(abs_file_path):
            print(f"NLP Engine: Keyword file not found at {abs_file_path}. Trying relative path: {file_path}")
            # Fallback to relative path if absolute not found (e.g. if running from root)
            if not os.path.exists(file_path):
                 print(f"NLP Engine: Keyword file still not found at relative path: {file_path}. Please check config.py and file location.")
                 return [] # Return empty list if file truly not found

            abs_file_path = file_path # Use relative path if it exists

        with open(abs_file_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
        print(f"NLP Engine: Loaded {len(keywords)} keywords from {file_path}")
    except FileNotFoundError:
        print(f"NLP Engine: Error: Keyword file not found at {abs_file_path} (or {file_path}).")
    except Exception as e:
        print(f"NLP Engine: An error occurred while loading keywords from {file_path}: {e}")
    return keywords

def detect_language_of_text(text):
    """
    Detects the language of the given text.
    Returns language code (e.g., 'en', 'es') or None if detection fails.
    """
    if not text or not isinstance(text, str):
        return None
    try:
        return detect(text)
    except LangDetectException: # Catch specific exception from langdetect
        # This can happen for short or ambiguous texts
        # print(f"NLP Engine: Could not detect language for text: '{text[:50]}...'")
        return None
    except Exception as e:
        print(f"NLP Engine: An unexpected error in language detection for text '{text[:50]}...': {e}")
        return None

def extract_entities(text, nlp_model):
    """Extracts named entities from text using a SpaCy model."""
    if not text or not nlp_model:
        return []
    try:
        doc = nlp_model(text)
        entities = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]: # Focus on specific entities
                entities.append({"text": ent.text, "label": ent.label_})
        return entities
    except Exception as e:
        print(f"NLP Engine: Error during entity extraction for text '{text[:50]}...': {e}")
        return []

def detect_keywords(text, keyword_list):
    """Detects if any keywords from the list are present in the text (case-insensitive)."""
    if not text or not keyword_list:
        return []

    # Ensure text is string and lowercased
    if not isinstance(text, str):
        # print(f"NLP Engine: detect_keywords expected string, got {type(text)}. Skipping.")
        return []
    text_lower = text.lower()

    found_keywords = [kw for kw in keyword_list if kw in text_lower] # Assumes keywords are already lowercase
    return found_keywords

def get_sentiment(text, sentiment_analyzer_instance):
    """Calculates sentiment scores for text using VADER."""
    if not text or not sentiment_analyzer_instance or not isinstance(text, str):
        return {} # Return empty dict if no text or analyzer
    try:
        return sentiment_analyzer_instance.polarity_scores(text)
    except Exception as e:
        print(f"NLP Engine: Error during sentiment analysis for text '{text[:50]}...': {e}")
        return {}

def calculate_risk_score(post_data_for_scoring):
    """Calculates a heuristic-based risk score."""
    score = 0

    # Keyword-based scoring
    hate_keywords = post_data_for_scoring.get('hate_speech_keywords', [])
    extremism_keywords = post_data_for_scoring.get('extremism_keywords', [])

    if hate_keywords:
        score += 40
        if len(hate_keywords) > 2: # More keywords, higher risk
            score += 15
        if len(hate_keywords) > 5:
            score += 10


    if extremism_keywords:
        score += 50
        if len(extremism_keywords) > 2:
            score += 20
        if len(extremism_keywords) > 5:
            score += 15

    # Sentiment-based scoring
    sentiment_compound = post_data_for_scoring.get('sentiment_compound_score', 0)
    if sentiment_compound < -0.7: # Very strong negative
        score += 20
    elif sentiment_compound < -0.4: # Strong negative
        score += 10
    elif sentiment_compound < -0.1: # Mild negative
        score += 5

    # Additional factors could be added here:
    # - Presence of specific entities (e.g., targeting a PERSON or ORG)
    # - Post length / verbosity if combined with negative sentiment/keywords
    # - User history (if available and relevant)

    return min(score, 100) # Cap score at 100

def analyze_posts(db, nlp_en_model, sentiment_analyzer, hate_speech_keywords_en, extremism_keywords_en):
    """
    Fetches posts, performs NLP analysis (language, NER, keywords, sentiment, risk score),
    and updates them in MongoDB.
    """
    if not db:
        print("NLP Engine: No database connection. Cannot analyze posts.")
        return

    posts_collection = db[POSTS_COLLECTION]
    # Query for posts that need analysis.
    # Example: posts where 'language' is set but 'ner_entities' or 'hate_speech_keywords' is missing.
    # Or, re-analyze posts older than a certain date.
    # For this iteration, let's focus on posts that have language detected but not other NLP fields.
    query = {
        "language": {"$exists": True, "$ne": None, "$nin": ["undetermined_no_text", "undetermined_detection_failed"]},
        "$or": [
            {"ner_entities": {"$exists": False}},
            {"hate_speech_keywords": {"$exists": False}},
            {"extremism_keywords": {"$exists": False}},
            {"sentiment": {"$exists": False}},
            {"risk_score": {"$exists": False}},
            # {"analysis_v2_timestamp": {"$exists": False}}
        ]
    }

    posts_to_analyze = list(posts_collection.find(query).limit(500)) # Limit for safety/dev

    if not posts_to_analyze:
        print("NLP Engine: No posts found requiring new NLP analysis (NER/Keywords/Sentiment/Risk) or all analyzed.")
        return

    print(f"NLP Engine: Found {len(posts_to_analyze)} posts for full NLP analysis.")

    operations = []
    processed_count = 0

    for post in posts_to_analyze:
        post_id = post["_id"]
        post_text = post.get("post_text")
        detected_language = post.get("language")

        update_fields = {
            # "analysis_v2_timestamp": datetime.utcnow() # Use a new timestamp for this analysis version
        }

        if not post_text:
            # This case should ideally be handled by the first analysis pass (language detection)
            # but as a safeguard:
            print(f"NLP Engine: Post ID {post_id} has no text. Skipping further NLP analysis.")
            # We might still want to update a timestamp if we add analysis_v2_timestamp
            # operations.append(UpdateOne({"_id": post_id}, {"$set": update_fields}))
            # processed_count +=1
            continue


        # --- Placeholder for Translation ---
        text_to_analyze = post_text
        # if detected_language and detected_language != 'en' and detected_language not in ["undetermined_no_text", "undetermined_detection_failed"]:
        #     print(f"NLP Engine: Post ID {post_id} is in '{detected_language}'. Translation to 'en' would be needed.")
        #     # translated_text = translate_text_function(post_text, target_language='en') # Placeholder
        #     # if translated_text:
        #     #     text_to_analyze = translated_text
        #     #     update_fields['translated_text_en'] = translated_text
        #     #     update_fields['original_language'] = detected_language # Already there
        #     # else:
        #     #     print(f"NLP Engine: Translation failed for post {post_id}. Analyzing original text if possible.")
        #     #     # If translation fails, we might skip NER/keyword for non-English if models are language-specific
        #     #     if detected_language != 'en': # Example: only process English for now if translation fails
        #     #         print(f"NLP Engine: Skipping EN-specific NLP for post {post_id} due to failed translation from {detected_language}")
        #     #         operations.append(UpdateOne({"_id": post_id}, {"$set": update_fields})) # Save at least timestamp
        #     #         processed_count +=1
        #     #         continue

        current_post_nlp_data = {} # To hold data for risk scoring

        # --- NER, Keyword, Sentiment (currently English specific or VADER for English-like) ---
        if detected_language == 'en': # Prioritize English for SpaCy and VADER's strength
            if nlp_en_model:
                entities = extract_entities(text_to_analyze, nlp_en_model)
                if entities:
                    update_fields['ner_entities'] = entities
                    current_post_nlp_data['ner_entities'] = entities
                    print(f"NLP Engine: Post ID {post_id} - Extracted {len(entities)} entities.")

            found_hate_keywords = detect_keywords(text_to_analyze.lower(), hate_speech_keywords_en)
            if found_hate_keywords:
                update_fields['hate_speech_keywords'] = found_hate_keywords
                current_post_nlp_data['hate_speech_keywords'] = found_hate_keywords
                print(f"NLP Engine: Post ID {post_id} - Found hate speech keywords: {found_hate_keywords}")

            found_extremism_keywords = detect_keywords(text_to_analyze.lower(), extremism_keywords_en)
            if found_extremism_keywords:
                update_fields['extremism_keywords'] = found_extremism_keywords
                current_post_nlp_data['extremism_keywords'] = found_extremism_keywords
                print(f"NLP Engine: Post ID {post_id} - Found extremism keywords: {found_extremism_keywords}")

            if sentiment_analyzer:
                sentiment_scores = get_sentiment(text_to_analyze, sentiment_analyzer)
                if sentiment_scores:
                    update_fields['sentiment'] = sentiment_scores
                    current_post_nlp_data['sentiment_compound_score'] = sentiment_scores.get('compound', 0)
                    print(f"NLP Engine: Post ID {post_id} - Sentiment (compound): {sentiment_scores.get('compound')}")

        elif detected_language and sentiment_analyzer: # Attempt VADER on other languages (quality may vary)
            print(f"NLP Engine: Post ID {post_id} is in '{detected_language}'. Attempting VADER (quality may vary). Skipping SpaCy EN NER/Keywords.")
            sentiment_scores = get_sentiment(text_to_analyze, sentiment_analyzer)
            if sentiment_scores:
                update_fields['sentiment'] = sentiment_scores
                current_post_nlp_data['sentiment_compound_score'] = sentiment_scores.get('compound', 0)
                print(f"NLP Engine: Post ID {post_id} ({detected_language}) - Sentiment (compound): {sentiment_scores.get('compound')}")

        elif not nlp_en_model and detected_language == 'en':
            print(f"NLP Engine: Post ID {post_id} is in English, but EN NLP model not available. Skipping NER/Keywords.")

        # Calculate Risk Score based on available data for this post
        risk_score = calculate_risk_score(current_post_nlp_data)
        update_fields['risk_score'] = risk_score
        print(f"NLP Engine: Post ID {post_id} - Calculated Risk Score: {risk_score}")

        update_fields["analysis_timestamp"] = datetime.utcnow()

        if len(update_fields) > 1 or 'risk_score' in update_fields : # Update if risk score or other nlp fields were added
             operations.append(UpdateOne({"_id": post_id}, {"$set": update_fields}))
        processed_count += 1

        # Perform bulk update in batches
        if len(operations) >= 100: # Batch size of 100
            try:
                posts_collection.bulk_write(operations)
                print(f"NLP Engine: Bulk updated {len(operations)} posts in MongoDB.")
                operations = [] # Reset batch
            except Exception as e:
                print(f"NLP Engine: Error during MongoDB bulk update: {e}")
                # Decide on error handling: stop, or skip this batch and continue?
                # For now, we'll print error and continue with next batches.
                operations = [] # Clear operations that failed

    # Update any remaining operations
    if operations:
        try:
            posts_collection.bulk_write(operations)
            print(f"NLP Engine: Bulk updated remaining {len(operations)} posts in MongoDB.")
        except Exception as e:
            print(f"NLP Engine: Error during final MongoDB bulk update: {e}")

    print(f"NLP Engine: Full NLP analysis (NER/Keywords/Sentiment/Risk) completed/attempted for {processed_count} posts.")


if __name__ == "__main__":
    print("NLP Engine: Initializing NLP models...")
    initialize_nlp_models() # Load SpaCy EN model and VADER

    print("NLP Engine: Starting analysis process...")
    db = get_db_connection(MONGO_URI, DB_NAME)

    if db:
        # Load keywords once
        print("NLP Engine: Loading keywords...")
        hate_keywords_en = load_keywords(HATE_SPEECH_KEYWORDS_FILE_EN)
        extremism_keywords_en = load_keywords(EXTREMISM_KEYWORDS_FILE_EN)

        # Call analyze_posts with all necessary components
        # NLP_MODEL_EN and SENTIMENT_ANALYZER are global and modified by initialize_nlp_models()
        analyze_posts(db, NLP_MODEL_EN, SENTIMENT_ANALYZER, hate_keywords_en, extremism_keywords_en)

    else:
        print("NLP Engine: Could not connect to database. Exiting.")

    print("NLP Engine: Analysis process finished.")
