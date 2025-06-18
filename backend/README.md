# Backend Service (FastAPI)

## Overview

This service provides the RESTful API for the OSINT platform. It's built using FastAPI and interacts with the MongoDB database to serve data to the frontend and potentially other clients.

## Key Features

*   User authentication (registration, login) using JWT.
*   Endpoints for querying scraped posts and profiles with filtering and pagination.
*   Analytics endpoints for aggregated data (risk scores, entities, language distribution, time series).
*   Automatic OpenAPI documentation available at `/docs` and ReDoc at `/redoc` when the service is running.

## Environment Variables

This service uses the following environment variables, typically configured in the root `.env` file and passed via `docker-compose.yml`:

*   `MONGO_URI`: MongoDB connection string (e.g., `mongodb://mongo:27017/facebook_data` when run with Docker Compose, or `mongodb://localhost:27017/facebook_data` for local development against a local MongoDB).
*   `DB_NAME`: MongoDB database name (e.g., `facebook_data`).
*   `POSTS_COLLECTION`: Name of the MongoDB collection for posts (e.g., `posts`).
*   `PROFILES_COLLECTION`: Name of the MongoDB collection for profiles (e.g., `profiles`).
*   `USERS_COLLECTION`: Name of the MongoDB collection for users (e.g., `users`).
*   `SECRET_KEY`: A strong secret key for JWT token generation. This **must** be set to a secure random string in production.
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiry time for access tokens in minutes (e.g., `30`).

## Running Standalone (for Development)

1.  **MongoDB**: Ensure a MongoDB instance is running and accessible. You can run MongoDB locally or use a Docker container.
    ```bash
    # Example: Run MongoDB in Docker for local development
    docker run -d -p 27017:27017 --name local-mongo mongo:5.0
    ```

2.  **Environment Setup**:
    *   It's recommended to use a virtual environment for Python:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Set the required environment variables. You can create a `.env` file in the `backend` directory (this is `.gitignore`d by default in the root `.dockerignore`, but for local dev it's fine) or export them directly into your shell:
        ```env
        # Example for a local .env file in backend/
        MONGO_URI="mongodb://localhost:27017/facebook_data_dev"
        DB_NAME="facebook_data_dev"
        POSTS_COLLECTION="posts"
        PROFILES_COLLECTION="profiles"
        USERS_COLLECTION="users"
        SECRET_KEY="your_local_dev_secret_key_here" # Can be simpler for local dev, but keep it secret
        ACCESS_TOKEN_EXPIRE_MINUTES=60
        ```
        *Note: The root `.env` file is used by `docker-compose`. For standalone local development, you might manage environment variables differently (e.g., a local `.env` file loaded by `python-dotenv` if `main.py` is modified to load it, or by shell exports).*

3.  **Install Dependencies**:
    Navigate to the `backend` directory and install requirements:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Development Server**:
    Still within the `backend` directory:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload` enables auto-reloading on code changes.
    *   `--host 0.0.0.0` makes the server accessible from your local network (not just `localhost`).
    *   `--port 8000` is the default port.

5.  **Access API**:
    *   The API will be available at `http://localhost:8000`.
    *   Interactive API documentation (Swagger UI): `http://localhost:8000/docs`.
    *   Alternative API documentation (ReDoc): `http://localhost:8000/redoc`.

This setup allows for development and testing of the backend service independently of Docker Compose if needed. Remember to manage your environment variables securely.
