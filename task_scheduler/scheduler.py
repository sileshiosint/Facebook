import time
import subprocess
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from config import SCHEDULE_INTERVAL_MINUTES, USER_AGENTS, PROXIES

# Make sure the script path is correct. Assuming task_scheduler and facebook_scraper are sibling directories.
# Adjust if your project structure is different.
SCRAPER_SCRIPT_PATH = "../facebook_scraper/scraper.py"

def run_scraper_job():
    print(f"Scheduler: Starting job at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    selected_user_agent = None
    if USER_AGENTS:
        selected_user_agent = random.choice(USER_AGENTS)
        print(f"Scheduler: Selected User-Agent: {selected_user_agent}")
    else:
        print("Scheduler: No User-Agents configured.")

    selected_proxy = None
    if PROXIES:
        # Simple rotation for now, could be random or more complex
        # This state should ideally be managed if multiple schedulers/jobs run
        # For a single job, this basic rotation is okay.
        current_proxy_index = getattr(run_scraper_job, 'current_proxy_index', -1)
        current_proxy_index = (current_proxy_index + 1) % len(PROXIES)
        selected_proxy = PROXIES[current_proxy_index]
        run_scraper_job.current_proxy_index = current_proxy_index # Store for next run
        print(f"Scheduler: Selected Proxy: {selected_proxy}")
    else:
        print("Scheduler: No Proxies configured.")

    command = ["python", SCRAPER_SCRIPT_PATH]
    if selected_user_agent:
        command.extend(["--user-agent", selected_user_agent])
    if selected_proxy:
        command.extend(["--proxy", selected_proxy])

    print(f"Scheduler: Constructing command: {' '.join(command)}")

    try:
        # Execute the scraper script
        # Using subprocess.PIPE to capture output, text=True for string output
        # Timeout for the subprocess can be added if needed e.g., timeout=1800 (30 mins)
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Scheduler: Scraper script stdout:")
        print(process.stdout)
        if process.stderr:
            print("Scheduler: Scraper script stderr:")
            print(process.stderr)
        print("Scheduler: Scraper job finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Scheduler: Scraper script execution failed with return code {e.returncode}")
        print("Scheduler: Scraper script stdout:")
        print(e.stdout)
        print("Scheduler: Scraper script stderr:")
        print(e.stderr)
    except FileNotFoundError:
        print(f"Scheduler: Error: Scraper script not found at {SCRAPER_SCRIPT_PATH}. Please check the path.")
    except Exception as e:
        print(f"Scheduler: An unexpected error occurred while running the scraper job: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC") # Or your local timezone string

    print(f"Scheduler: Initializing. Scraper job will run every {SCHEDULE_INTERVAL_MINUTES} minutes.")
    print(f"Scheduler: Configured User Agents count: {len(USER_AGENTS)}")
    print(f"Scheduler: Configured Proxies count: {len(PROXIES)}")
    if PROXIES:
        print(f"Scheduler: Proxies: {PROXIES}")

    # Run once immediately, then schedule
    # run_scraper_job()

    scheduler.add_job(run_scraper_job, 'interval', minutes=SCHEDULE_INTERVAL_MINUTES)

    print("Scheduler: Starting scheduler. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler: Shutting down...")
        pass
