# NLP Analysis Engine Module

## Overview

This module is responsible for processing text data scraped from Facebook. It reads posts from the MongoDB database, performs various Natural Language Processing (NLP) tasks, and updates the post records in MongoDB with the derived analytical insights.

## Key Features

*   **Language Detection**: Identifies the language of post text using `langdetect`.
*   **Named Entity Recognition (NER)**: Extracts predefined entities (PERSON, ORG, GPE, LOC) from English text using the `en_core_web_sm` SpaCy model.
*   **Sentiment Analysis**: Calculates sentiment scores (positive, negative, neutral, compound) for English text (and attempts other languages) using VADER (`vaderSentiment`).
*   **Hate Speech & Extremism Keyword Spotting**:
    *   Identifies occurrences of user-defined keywords and phrases related to hate speech and extremism.
    *   Keyword lists for English are maintained in the `nlp_analysis_engine/keywords/` directory (e.g., `hate_speech_en.txt`, `extremism_en.txt`).
*   **Risk Scoring**: Assigns a heuristic-based risk score (0-100) to each post. The score is calculated based on the presence of detected keywords and the sentiment of the post.
*   **Data Enrichment**: Updates MongoDB post records with new fields: `language`, `ner_entities`, `sentiment`, `hate_speech_keywords`, `extremism_keywords`, `risk_score`, and `analysis_timestamp`.
*   **Batch Processing**: Processes posts in batches to efficiently update MongoDB.

## Environment Variables

This module is configured via environment variables, typically set in the root `.env` file and passed through `docker-compose.yml`:

*   `MONGO_URI`: MongoDB connection string (e.g., `mongodb://mongo:27017/facebook_data`).
*   `DB_NAME`: Name of the MongoDB database (e.g., `facebook_data`).
*   `POSTS_COLLECTION`: Name of the MongoDB collection where posts are stored and updated (e.g., `posts`).

## Keyword Customization

To customize keyword-based detection:
1.  Edit the text files in the `nlp_analysis_engine/keywords/` directory.
2.  Add one keyword or phrase per line.
3.  Keywords are matched case-insensitively.
4.  Currently, only English keyword files are implemented (`hate_speech_en.txt`, `extremism_en.txt`). To support other languages, new keyword files and corresponding logic in `analyzer.py` would be needed.

## Running

This module is designed to be run as a service (e.g., within a Docker container managed by `docker-compose.yml`). When the service starts, `analyzer.py` is executed. It will periodically query MongoDB for posts that require NLP analysis, process them, and update the database.

### Standalone Execution (for Development/Testing)

1.  **MongoDB**: Ensure a MongoDB instance is running and accessible with scraped data.
2.  **Environment Variables**: Set the required environment variables (`MONGO_URI`, `DB_NAME`, `POSTS_COLLECTION`) in your shell or a local `.env` file (ensure `python-dotenv` is used in `analyzer.py` if relying on a local `.env` file).
3.  **Install Dependencies**:
    Navigate to the `nlp_analysis_engine` directory and install requirements:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download SpaCy Model**:
    If you haven't already, download the English SpaCy model used by the engine:
    ```bash
    python -m spacy download en_core_web_sm
    ```
5.  **Run the Analyzer**:
    ```bash
    # From within nlp_analysis_engine directory
    python analyzer.py
    ```
    The script will connect to MongoDB, process posts, and print logs to the console. It's designed to run once and exit; for continuous operation, it would typically be run by a higher-level scheduler or a loop within the script if not containerized with a restart policy. In the Docker Compose setup, it runs as a service that completes its task and can be restarted or run periodically depending on orchestration needs (though current setup is `restart: unless-stopped`, meaning it will run once and then stop until restarted, or it would need an internal loop to keep checking for new data).

## Dependencies
Listed in `requirements.txt`:
*   `pymongo`: For MongoDB interaction.
*   `python-dotenv`: For environment variable management.
*   `langdetect`: For language detection.
*   `spacy`: For NLP tasks like NER. (Requires model download, e.g., `en_core_web_sm`)
*   `vaderSentiment`: For sentiment analysis.
