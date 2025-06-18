# OSINT Data Collection and Analysis Platform (Ethical Use Only)

## Project Overview

This project is a modular open-source tool designed for collecting and analyzing publicly visible Facebook data. Its primary purpose is for authorized analysts in areas like threat intelligence, disinformation tracking, and hate speech monitoring, strictly for ethical public safety and research purposes.

**IMPORTANT: This tool should ONLY be used in compliance with all applicable laws, regulations, and Facebook's terms of service. Unauthorized or unethical use is strictly prohibited.**

## Core Components

*   **Facebook Scraper**: Python-based scraper using `undetected-chromedriver` and `selenium` to gather data from public Facebook groups, pages, and profiles (without using the Facebook Graph API).
*   **Background Task Scheduler**: Uses `APScheduler` to run recurring scraping jobs, with features like user-agent rotation and proxy support.
*   **NLP + AI Analysis Engine**: Processes scraped text for language detection, Named Entity Recognition (NER), hate speech/extremism keyword spotting, sentiment analysis, and risk scoring.
*   **FastAPI Backend**: Provides a RESTful API to access the scraped and analyzed data, with token-based authentication.
*   **React Frontend Dashboard**: A web interface for viewing data, analytics, and managing the system.
*   **MongoDB**: Used as the primary data store.
*   **Docker + Compose**: The entire system is containerized for ease of deployment.

## Ethical Use Guidelines

*   **Lawful Purpose**: Only use this tool for lawful and ethical purposes, such as academic research, journalism, or activities aimed at public safety by authorized organizations.
*   **Respect Privacy**: Focus on publicly available information. Avoid attempts to access private data or circumvent privacy settings.
*   **Data Minimization**: Collect only the data necessary for the specific research or monitoring task.
*   **Secure Storage**: Protect collected data with strong security measures. Ensure compliance with data protection regulations (e.g., GDPR, CCPA) if applicable.
*   **Transparency**: If findings are published, be transparent about the methods used and the data's origin, while protecting individuals' privacy.
*   **No Misuse**: Do not use this tool for spamming, harassment, spreading misinformation, or any malicious activities.

## Prerequisites

*   Docker Engine (latest version recommended)
*   Docker Compose (latest version recommended)
*   Git (for cloning the repository)

## Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd <repository_directory> # Replace <repository_directory> with the cloned folder name
    ```

2.  **Configure Environment Variables**:
    *   Copy the example environment file located in the project root:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file in the project root and fill in all required values, especially:
        *   `MONGO_URI` (if different from default `mongodb://mongo:27017/facebook_data` when running in Docker)
        *   `DB_NAME`
        *   `SECRET_KEY` for the backend (generate a strong one, e.g., `openssl rand -hex 32`)
        *   `FACEBOOK_EMAIL` and `FACEBOOK_PASSWORD` for the scraper.
        *   Other variables as needed (see `.env.example` for details).

3.  **Build and Run with Docker Compose**:
    *   From the project root directory, run:
        ```bash
        docker-compose up --build -d
        ```
    *   The `-d` flag runs the services in detached mode.
    *   The first build may take some time as it downloads base images and installs dependencies.

4.  **Accessing Services**:
    *   **Frontend Dashboard**: `http://localhost:8080` (or as configured in `docker-compose.yml` for the frontend service port)
    *   **Backend API Docs**: `http://localhost:8000/docs` (or as configured for the backend service port)
    *   **MongoDB**: Accessible on `mongodb://localhost:27017` from your host machine if you need direct access (this port is mapped in `docker-compose.yml`).

## Stopping the Application

*   To stop all running services:
    ```bash
    docker-compose down
    ```
*   To stop and remove volumes (deletes MongoDB data and other persisted data):
    ```bash
    docker-compose down -v
    ```

## Project Structure

*   `backend/`: FastAPI application providing the API.
*   `frontend/`: React application for the user dashboard.
*   `facebook_scraper/`: Python scripts and utilities for scraping Facebook data.
*   `nlp_analysis_engine/`: Python scripts for NLP processing of scraped data.
*   `task_scheduler/`: Python service for scheduling scraping tasks.
*   `docs/`: (This directory was created but not used yet) For future detailed documentation, architecture diagrams, etc.

---
*This tool is intended for responsible use by professionals. Users are solely responsible for adhering to all legal and ethical standards.*
