# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies that might be needed by some Python packages
# e.g., for cryptography or database drivers. Add as necessary.
# Example for psycopg2 (PostgreSQL driver) or other compiled libraries:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Ensure the .env file is not copied into the image for security.
# Configurations will be passed via docker-compose environment variables.

EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# Ensure main:app points to your FastAPI instance within the backend directory structure
# If main.py is in the root of the copied backend code (e.g. /app/main.py), this is correct.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
