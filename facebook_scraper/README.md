# Facebook Scraper Module

## Overview

This module is responsible for scraping publicly available data from Facebook. It uses `selenium` with `undetected-chromedriver` to mimic a real browser session, allowing it to access content visible to a logged-in user without using the official Facebook Graph API.

**Note**: This scraper should be used responsibly and ethically, adhering to all relevant laws and Facebook's Terms of Service. Unauthorized data scraping can lead to account restrictions or legal consequences.

## Key Features

*   Logs into Facebook using provided credentials (sourced from environment variables via the task scheduler).
*   Scrapes public group posts, page posts, and basic profile information based on keywords.
    *   Searches for groups and pages by keyword.
    *   Extracts URLs of found groups/pages.
    *   Visits individual group/page URLs to scrape posts.
*   Extracts various data points from posts:
    *   Post text content.
    *   Post timestamp.
    *   User details (name of the poster, user ID if available from profile links).
    *   Reaction counts (simplified total count).
    *   Comment counts.
    *   Post URL.
    *   Group/Page name and URL where the post originated.
*   Designed to be executed by the `task_scheduler` module.
*   Accepts user-agent string and proxy server configuration as command-line arguments (passed by the scheduler).
*   Incorporates randomized delays between actions to make scraping patterns less predictable and reduce the likelihood of detection.
*   Stores scraped data (posts and basic profiles) into a MongoDB database, using collections defined by environment variables.

## Configuration (via Task Scheduler)

The scraper script (`scraper.py`) is configured through a combination of environment variables (for sensitive data like credentials and DB URIs) and command-line arguments (for operational parameters like user-agent and proxy). These are typically managed and passed by the `task_scheduler` service when it invokes the scraper.

Key configurations sourced from environment variables (via the calling environment of the scheduler):
*   `FACEBOOK_EMAIL`: Email address for Facebook login.
*   `FACEBOOK_PASSWORD`: Password for Facebook login.
*   `MONGO_URI`: MongoDB connection string.
*   `DB_NAME`: Name of the MongoDB database.
*   `POSTS_COLLECTION`: Name of the collection where post data is stored.
*   `PROFILES_COLLECTION`: Name of the collection where basic profile data (name, URL, search keyword) is stored.

Command-line arguments accepted by `scraper.py`:
*   `--user-agent <USER_AGENT_STRING>`: Sets the user-agent for the browser.
*   `--proxy <PROXY_STRING>`: Sets a proxy server (e.g., `http://host:port`).

## Usage

This module is not designed to be run standalone for routine operations. It is intended to be invoked by the `task_scheduler/scheduler.py` script. The scheduler handles the periodic execution, passing the necessary operational parameters for each run.

For development or testing, you can run `scraper.py` directly from the `facebook_scraper` directory if you have Python and the required dependencies installed, and environment variables are set:
```bash
# Ensure you are in the facebook_scraper directory
# Set environment variables (FACEBOOK_EMAIL, FACEBOOK_PASSWORD, MONGO_URI, DB_NAME etc.)
# Example:
# export FACEBOOK_EMAIL="your_email"
# export FACEBOOK_PASSWORD="your_password"
# ...
# python scraper.py --user-agent "Some User Agent"
# (Add --proxy if needed)
```
However, running within the Dockerized environment via the scheduler is the intended operational mode.

## Dependencies
Listed in `requirements.txt`:
*   `selenium`
*   `undetected-chromedriver`
*   `pymongo`
*   `python-dotenv` (primarily for local testing, in Docker these are environment variables)
