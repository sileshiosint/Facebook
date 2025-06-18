# Task Scheduler Module

## Overview

This module orchestrates the execution of Facebook scraping tasks using `APScheduler`. It is responsible for periodically running the `facebook_scraper/scraper.py` script, managing dynamic configurations like user-agents and proxies for each scraping job.

## Key Features

*   **Scheduled Execution**: Periodically triggers the Facebook scraper based on a configurable interval.
*   **Dynamic Configuration**:
    *   Rotates through a predefined list of user-agent strings for each scraper run.
    *   Supports using a list of proxies, rotating through them for different scraper runs.
*   **Parameter Passing**: Passes the selected user-agent and proxy to the `scraper.py` script via command-line arguments.
*   **Environment Variable Management**: Relies on environment variables (typically set via `docker-compose` from a root `.env` file) for sensitive information like Facebook credentials and MongoDB connection details, which are then implicitly available to the scraper script it executes.

## Environment Variables

This module, and by extension the scraper it runs, is configured via environment variables defined in the root `.env` file and passed through `docker-compose.yml`:

*   `SCHEDULE_INTERVAL_MINUTES`: Defines how often the scraping task is run (e.g., `120` for every 2 hours).
*   `PROXIES_LIST`: An optional comma-separated list of proxy server strings (e.g., `http://user1:pass1@proxy1.com:port,http://user2:pass2@proxy2.com:port`). If empty, no proxy is used.
*   `USER_AGENTS`: Defined directly in `task_scheduler/config.py` but could be moved to environment variables if more dynamic configuration is needed.
*   All environment variables required by `facebook_scraper/scraper.py` must also be available in the execution environment of this scheduler. These include:
    *   `FACEBOOK_EMAIL`
    *   `FACEBOOK_PASSWORD`
    *   `MONGO_URI`
    *   `DB_NAME`
    *   `POSTS_COLLECTION`
    *   `PROFILES_COLLECTION`

## Running

This module is designed to be run as a long-running service, typically within a Docker container managed by `docker-compose.yml`. When the container starts, `scheduler.py` is executed, which initializes and starts the APScheduler. The scheduler then takes over and triggers the scraping jobs at the specified intervals.

### Standalone Execution (for Development/Testing)

While primarily intended for Docker, you can run `scheduler.py` standalone for development, provided the `facebook_scraper` module is correctly located (e.g., in the parent directory as `../facebook_scraper/`).

1.  **Directory Structure**: Ensure `facebook_scraper` is accessible relative to `task_scheduler`.
    ```
    project_root/
    ├── task_scheduler/
    │   ├── scheduler.py
    │   └── ...
    └── facebook_scraper/
        └── scraper.py
        └── ...
    ```
2.  **Environment Variables**: Set all required environment variables (as listed above) in your shell or a local `.env` file (ensure `python-dotenv` is used in `scheduler.py` if relying on a local `.env` file for standalone runs, which it currently does via its `config.py`).
3.  **Install Dependencies**:
    Install requirements for both the scheduler and the scraper:
    ```bash
    # From within task_scheduler directory
    pip install -r requirements.txt
    pip install -r ../facebook_scraper/requirements.txt
    ```
4.  **Run the Scheduler**:
    ```bash
    # From within task_scheduler directory
    python scheduler.py
    ```
    The scheduler will then print logs to the console indicating when jobs are being run.

## Dependencies
*   `APScheduler`: For scheduling tasks.
*   `python-dotenv`: For managing environment variables from a `.env` file (especially useful for local development).
*   The dependencies of `facebook_scraper` are also indirectly required for the successful execution of scraping jobs. These are installed in the Docker image.
