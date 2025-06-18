# nlp_analysis_engine/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any (e.g., for specific ML model backends or text processing libraries)
# For example, libgomp1 is sometimes needed by NLP libraries that use OpenMP
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgomp1 \
#  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Download SpaCy models
# This should match the model used in your analyzer.py (e.g., en_core_web_sm)
# This step requires internet access during the build.
RUN python -m spacy download en_core_web_sm

COPY . /app

# Environment variables for MongoDB URI, etc., will be passed via docker-compose.
# Ensure analyzer.py can correctly import from config.py and access keywords/ directory.
# The WORKDIR is /app, and keywords/ should be at /app/keywords/ if copied correctly.

CMD ["python", "analyzer.py"]
