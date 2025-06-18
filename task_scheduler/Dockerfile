# task_scheduler/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Chromium browser. undetected-chromedriver will attempt to download
# a compatible ChromeDriver if it finds the browser.
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    # Add other essential build tools or libraries if required by dependencies
    # build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements for both scheduler and scraper
COPY ./requirements.txt /app/task_scheduler_requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/task_scheduler_requirements.txt

# Ensure facebook_scraper requirements are also installed
# Assuming facebook_scraper/requirements.txt exists and is correct
COPY ../facebook_scraper/requirements.txt /app/facebook_scraper_requirements.txt
RUN pip install --no-cache-dir -r /app/facebook_scraper_requirements.txt

# Copy the scheduler application code
COPY . /app/task_scheduler

# Copy the Facebook scraper application code
# This makes the facebook_scraper module available to the scheduler
COPY ../facebook_scraper /app/facebook_scraper

# Set the working directory to where scheduler.py is
WORKDIR /app/task_scheduler

# Environment variables for Facebook credentials, MongoDB URI, etc.,
# will be passed via docker-compose.
# Ensure scraper.py can correctly import from .config and .utils
# when called by scheduler.py from this WORKDIR.
# Python's import system should handle this if /app is implicitly on PYTHONPATH
# or if using relative imports correctly within the facebook_scraper module.
# Setting PYTHONPATH explicitly can also help if imports fail.
# ENV PYTHONPATH="/app:$PYTHONPATH"

CMD ["python", "scheduler.py"]
