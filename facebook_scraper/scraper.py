import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re # For extracting user ID
import random # For random delays (though used via utils.random_delay)
# time is already imported in utils.random_delay, but good practice if directly used.

import argparse # Added for CLI arguments
# Assuming config.py is in the same directory and loads environment variables
from .config import FACEBOOK_EMAIL, FACEBOOK_PASSWORD
from .utils import get_db_connection, random_delay # Import random_delay

def initialize_driver(user_agent=None, proxy=None):
    """Initializes and returns an undetected_chromedriver instance."""
    options = uc.ChromeOptions() # Use uc.ChromeOptions for undetected_chromedriver

    options.add_argument("--disable-notifications")
    # The following option can help with some anti-scraping measures by Facebook
    options.add_argument('--accept-language=en-US,en;q=0.9')
    # options.add_argument("--headless") # Optional: run in headless mode

    if user_agent:
        print(f"Scraper: Using User-Agent: {user_agent}")
        options.add_argument(f'--user-agent={user_agent}')
    if proxy:
        print(f"Scraper: Using Proxy: {proxy}")
        options.add_argument(f'--proxy-server={proxy}')
        # Note: For authenticated proxies with undetected_chromedriver,
        # it might require more complex setup if '--proxy-server=http://user:pass@host:port' doesn't work directly.
        # Sometimes, a proxy extension like Chrome's SwitchyOmega, configured by Selenium, is needed for auth.
        # For now, assuming unauthenticated or that the format works.

    driver = uc.Chrome(options=options)
    driver.set_window_size(1200, 800) # Setting a reasonable window size
    return driver

def login_to_facebook(driver, email, password):
    """Logs into Facebook using the provided credentials."""
    if not email or not password:
        print("Facebook email or password not provided. Skipping login.")
        return False

    print(f"Attempting to log in to Facebook with email: {email}")
    driver.get("https://www.facebook.com")

    try:
        # Handle potential cookie consent pop-ups first
        cookie_buttons = driver.find_elements(By.XPATH, "//div[@aria-label=' μόνο βασικά cookie' or @aria-label='Allow all cookies' or @aria-label='Allow essential and optional cookies']/ancestor::div[@role='button']")
        if cookie_buttons:
            for btn in cookie_buttons:
                try:
                    # Try to click the most permissive one if multiple exist, otherwise any
                    if "all" in btn.text.lower() or "allow" in btn.text.lower() :
                         btn.click()
                         print("Clicked a cookie consent button.")
                         WebDriverWait(driver, 5).until_not(EC.visibility_of(btn))
                         break
                except Exception as e:
                    print(f"Could not click cookie button: {e}")
            # Fallback if specific text not found, click the first one
            if not any("Clicked a cookie consent button." in log for log in ["log"]): # hack to check if clicked
                 try:
                    cookie_buttons[0].click()
                    print("Clicked the first cookie consent button found.")
                    WebDriverWait(driver, 5).until_not(EC.visibility_of(cookie_buttons[0]))
                 except Exception as e:
                    print(f"Fallback cookie button click failed: {e}")


        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(email)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pass"))
        )
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "login"))
        )
        login_button.click()

        # Wait for either a successful login indicator or a failure indicator
        WebDriverWait(driver, 20).until(
            lambda d: EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home'], div#loginform, div[role='main']"))(d)
        )

        time.sleep(2) # Give a bit of time for redirects or elements to settle

        current_url = driver.current_url
        if "login" in current_url and "home.php" not in current_url :
            if "checkpoint" in current_url:
                print("Login resulted in a security checkpoint.")
                return False
            print("Login failed. Still on login page or redirected to a login-related page.")
            error_message_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='alert'], ._9ay7")
            if error_message_elements:
                for error_el in error_message_elements:
                    if error_el.text:
                        print(f"Facebook error message: {error_el.text}")
                        break
            return False
        else:
            # Check for a common element that indicates logged-in state, e.g., profile picture link
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='profile.php?id=']")) # Common link for profile
                )
                print("Login likely successful (found profile link).")
                return True
            except TimeoutException:
                 # Fallback: Check for "Home" aria-label, which is common on logged-in pages
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home']")))
                    print("Login likely successful (found 'Home' link).")
                    return True
                except TimeoutException:
                    print("Login status uncertain. Could not confirm key post-login elements.")
                    # driver.save_screenshot("login_uncertain_screenshot.png")
                    return False # Treat as failure if positive confirmation is missing

    except Exception as e:
        print(f"An error occurred during login: {e}")
        # driver.save_screenshot("login_error_screenshot.png")
        return False

def search_facebook_groups(driver, keyword):
    """Searches for Facebook groups based on a keyword."""
    search_url = f"https://www.facebook.com/search/groups/?q={keyword}"
    print(f"Navigating to group search: {search_url}")
    driver.get(search_url)
    random_delay(1, 2) # Small delay after page load
    group_urls = []
    try:
        # Wait for search results to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Search results')]//a[contains(@href, '/groups/')] | //div[@role='feed']//a[contains(@href, '/groups/')]"))
        )
        print(f"Successfully navigated to search results for '{keyword}'.")
        random_delay(0.5, 1.5) # Delay after elements found

        # Find all links that potentially point to groups
        # This selector looks for <a> tags with href containing "/groups/" and often within a heading or specific structure.
        # It's broad and might need refinement.
        group_link_elements = driver.find_elements(By.XPATH, "//div[@aria-label='Search results']//a[contains(@href, '/groups/') and .//span[string-length(text()) > 0]] | //div[contains(@class,'x1yztbdb')]//a[contains(@href,'/groups/') and not(contains(@href,'/search/'))]")

        print(f"Found {len(group_link_elements)} potential group link elements.")

        unique_urls = set()
        for link_el in group_link_elements:
            href = link_el.get_attribute('href')
            if href and "/groups/" in href:
                # Clean up URL parameters like tracking info
                cleaned_url = href.split('?')[0]
                if cleaned_url.endswith('/'):
                    cleaned_url = cleaned_url[:-1]

                # Further check to avoid non-group links if possible (e.g. links to create group)
                if "/groups/create/" not in cleaned_url and cleaned_url not in unique_urls:
                    # Check if the link text or surrounding text indicates it's a group
                    # This is heuristic. A more reliable way is to check the page it links to, but that's too slow here.
                    # link_text = link_el.text or ""
                    # parent_text = link_el.find_element(By.XPATH, "..").text or ""
                    # if "group" in link_text.lower() or "group" in parent_text.lower() or link_el.is_displayed(): # Basic check
                    unique_urls.add(cleaned_url)
                    print(f"Found group URL: {cleaned_url}")

        group_urls = list(unique_urls)[:5] # Limit to top 5 unique URLs for now
        print(f"Extracted {len(group_urls)} unique group URLs: {group_urls}")
        # driver.save_screenshot(f"search_results_{keyword}.png")

    except TimeoutException:
        print(f"Timeout waiting for search results for '{keyword}'. The page might be empty or structure changed.")
        # driver.save_screenshot(f"search_results_timeout_{keyword}.png")
    except Exception as e:
        print(f"An error occurred during group search navigation or URL extraction: {e}")

    return group_urls

# --- Page Scraping Functions ---

def search_facebook_pages(driver, keyword):
    """Searches for Facebook pages based on a keyword."""
    search_url = f"https://www.facebook.com/search/pages/?q={keyword}"
    print(f"Navigating to page search: {search_url}")
    driver.get(search_url)
    random_delay(1, 2) # Small delay after page load
    pages_data = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Search results')]//a[contains(@href, 'facebook.com/') and not(contains(@href, '/groups/'))] | //div[@role='feed']//a[contains(@href, 'facebook.com/') and not(contains(@href, '/groups/'))]"))
        )
        print(f"Successfully navigated to page search results for '{keyword}'.")
        random_delay(0.5, 1.5) # Delay after elements found

        # Selector for page links: <a> tags with a specific role or within a structure that denotes a page result.
        # This is highly generic and likely needs refinement.
        page_link_elements = driver.find_elements(By.XPATH, "//div[@aria-label='Search results']//div[contains(@class,'x1yztbdb')]//a[contains(@href,'facebook.com/') and not(contains(@href,'/groups/')) and not(contains(@href,'/search/')) and .//span[string-length(text()) > 0]]")

        print(f"Found {len(page_link_elements)} potential page link elements.")
        unique_pages = {} # Store url -> name to avoid duplicates by URL

        for link_el in page_link_elements:
            href = link_el.get_attribute('href')
            page_name_element = link_el.find_element(By.XPATH, ".//span[string-length(text()) > 0]") # Assuming name is in a span inside 'a'
            page_name = page_name_element.text.strip() if page_name_element else "Unknown Page"

            if href and page_name:
                cleaned_url = href.split('?')[0]
                if cleaned_url.endswith('/'):
                    cleaned_url = cleaned_url[:-1]

                if "/pages/" in cleaned_url or not any(s in cleaned_url for s in ["/groups/", "/events/", "/posts/", "/people/"]): # Basic filter
                    if cleaned_url not in unique_pages:
                         unique_pages[cleaned_url] = page_name
                         print(f"Found Page: {page_name} - URL: {cleaned_url}")

        # Convert to list of dicts and limit
        pages_data = [{"page_name": name, "page_url": url} for url, name in unique_pages.items()][:5]
        print(f"Extracted {len(pages_data)} unique pages: {pages_data}")

    except TimeoutException:
        print(f"Timeout waiting for page search results for '{keyword}'.")
    except Exception as e:
        print(f"An error occurred during page search or URL extraction: {e}")
    return pages_data

def scrape_page_posts(driver, page_url, page_name, keyword_search_term, db, num_scrolls=1):
    """Scrapes posts from a specific Facebook page."""
    print(f"Navigating to page: {page_url}")
    driver.get(page_url)
    random_delay(1.5, 3) # Delay after page navigation
    scraped_page_posts_data = []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='feed' or @aria-label='Page feed'] | //div[contains(@class, 'x1hc1fzr')] | //div[data-pagelet='ProfileTimeline']"))
        )
        print(f"Successfully navigated to page: {page_url}")
    except TimeoutException:
        print(f"Timeout waiting for page to load: {page_url}.")
        return []

    print(f"Scrolling {num_scrolls} times to load posts on page {page_name}...")
    for scroll_num in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scroll {scroll_num + 1}/{num_scrolls} completed.")
        random_delay(2, 4) # Increased delay after scroll for content to load

    # Selectors for page posts will be similar to group posts but might have slight variations
    post_elements = driver.find_elements(By.XPATH, "//div[@role='article'] | //div[data-visualcompletion=' μεγαλύτερη ανάρτηση'] | //div[contains(@class,'x1lliihq') and contains(@class,'x1plvlek')]") # x1lliihq x1plvlek are example classes
    print(f"Found {len(post_elements)} potential post elements on page {page_name}.")

    for i, post_el in enumerate(post_elements):
        random_delay(0.5, 1.5) # Short delay between processing each post
        print(f"\nProcessing post {i+1}/{len(post_elements)} on page {page_name}...")
        post_data = {
            "keyword_search_term": keyword_search_term,
            "source_type": "page",
            "page_name": page_name,
            "page_url": page_url,
            "post_url": None,
            "post_text": None,
            "post_time": None,
            "user_name": page_name, # For pages, the user is the page itself
            "user_id": page_url.split('/')[-1] if '/' in page_url else page_url, # Use page slug/ID as user_id for page
            "reactions": {"total": 0},
            "comment_count": 0,
            "scraped_timestamp": datetime.utcnow().isoformat()
        }

        # Extract Post Text (using similar selectors as group posts, may need adjustment)
        try:
            text_element = post_el.find_element(By.XPATH, ".//div[@data-ad-preview='message'] | .//div[contains(@class,'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')] | .//div[contains(@class,'x1iorvi4 x1pi30zi x1l90r2v x1swvt13')]//span[contains(@class, 'x193iq5w')]")
            if text_element: post_data["post_text"] = text_element.text.strip()
        except NoSuchElementException:
            print("Post text not found.")
        except Exception as e:
            print(f"Error extracting post text on page: {e}")

        # Extract Post Time and URL (similar selectors)
        try:
            time_link_el = post_el.find_element(By.XPATH, ".//a[contains(@href,'/posts/') or contains(@href,'/videos/') or contains(@href,'/photos/') or contains(@href,'?story_fbid=') or contains(@href, '/permalink/')][@aria-label or @title or contains(@class,'x1i10hfl')]")
            post_data["post_time"] = time_link_el.get_attribute("aria-label") or time_link_el.get_attribute("title") or time_link_el.text
            post_data["post_url"] = time_link_el.get_attribute("href")
        except NoSuchElementException:
            print("Post time/URL not found.")
        except Exception as e:
            print(f"Error extracting post time/URL on page: {e}")

        # Reactions and Comments (similar selectors)
        try:
            reaction_count_el = post_el.find_element(By.XPATH, ".//span[contains(@aria-label,'reaction') and string-length(text()) > 0 and number(translate(text(), 'KMBkmb', '')) = number(translate(text(), 'KMBkmb', ''))] | .//span[contains(@class,'xt0b8zv') and string-length(text()) > 0]")
            reaction_text = reaction_count_el.text.upper()
            num_part = re.match(r"[\d\.]+", reaction_text)
            if num_part:
                num = float(num_part.group(0))
                if "K" in reaction_text: num *= 1000
                elif "M" in reaction_text: num *= 1000000
                post_data["reactions"]["total"] = int(num)
        except NoSuchElementException:
            print("Reaction count not found.")
        except Exception as e:
            print(f"Error extracting reaction count on page: {e}")

        try:
            comment_count_el = post_el.find_element(By.XPATH, ".//div[contains(text(),'comment') or contains(text(),'Comment')] | .//span[contains(text(),'comment') or contains(text(),'Comment')]")
            match = re.search(r"(\d+)\s*(?:comment|bình luận)", comment_count_el.text, re.IGNORECASE)
            if match: post_data["comment_count"] = int(match.group(1))
        except NoSuchElementException:
            print("Comment count not found.")
        except Exception as e:
            print(f"Error extracting comment count on page: {e}")

        if post_data["post_text"] or post_data["post_url"]:
            print(f"Scraped page post: Text: {post_data['post_text'][:50] if post_data['post_text'] else 'N/A'}...")
            scraped_page_posts_data.append(post_data)
            if db: save_post_to_db(db, post_data) # Use the same save_post_to_db function
        else:
            print("Skipping page post as no significant data was extracted.")

    return scraped_page_posts_data

# --- Profile Scraping Functions ---

def search_facebook_profiles(driver, keyword):
    """Searches for Facebook profiles based on a keyword (very basic)."""
    search_url = f"https://www.facebook.com/search/people/?q={keyword}"
    print(f"Navigating to profile search: {search_url}")
    driver.get(search_url)
    random_delay(1, 2) # Small delay after page load
    profiles_data = []
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Search results')]//a[contains(@href, 'profile.php?id=') or (contains(@href,'facebook.com/') and not(contains(@href,'/groups/')) and not(contains(@href,'/pages/')) )] | //div[@role='feed']//a[contains(@href, 'profile.php?id=')]"))
        )
        print(f"Successfully navigated to profile search results for '{keyword}'.")
        random_delay(0.5, 1.5) # Delay after elements found

        # Selector for profile links - this is extremely generic for public search
        profile_link_elements = driver.find_elements(By.XPATH, "//div[@aria-label='Search results']//div[contains(@class,'x1yztbdb')]//a[contains(@href,'facebook.com/') and not(contains(@href,'/groups/')) and not(contains(@href,'/pages/')) and .//span[string-length(text()) > 0]]")

        print(f"Found {len(profile_link_elements)} potential profile link elements.")
        unique_profiles = {} # url -> name

        for link_el in profile_link_elements:
            href = link_el.get_attribute('href')
            name_element = link_el.find_element(By.XPATH, ".//span[string-length(text()) > 0]")
            name = name_element.text.strip() if name_element else "Unknown User"

            if href and name:
                cleaned_url = href.split('?')[0]
                if cleaned_url.endswith('/'): cleaned_url = cleaned_url[:-1]

                # Basic check to ensure it's a profile-like URL
                if "profile.php" in cleaned_url or not any(s in cleaned_url for s in ["/groups/", "/pages/", "/stories/", "/posts/", "/watch/", "/events/"]):
                    if cleaned_url not in unique_profiles:
                        unique_profiles[cleaned_url] = name
                        print(f"Found Profile: {name} - URL: {cleaned_url}")

        profiles_data = [{"user_name": name, "profile_url": url} for url, name in unique_profiles.items()][:5] # Limit to 5
        print(f"Extracted {len(profiles_data)} unique profiles: {profiles_data}")

    except TimeoutException:
        print(f"Timeout waiting for profile search results for '{keyword}'.")
    except Exception as e:
        print(f"An error occurred during profile search or URL extraction: {e}")
    return profiles_data

def save_profile_data_to_db(db, profile_data, keyword_search_term):
    """Saves basic profile data to the MongoDB 'profiles' collection."""
    if not db:
        print("Database connection not available. Skipping profile save.")
        return False

    data_to_save = {
        "keyword_search_term": keyword_search_term,
        "user_name": profile_data.get("user_name"),
        "profile_url": profile_data.get("profile_url"),
        "scraped_timestamp": datetime.utcnow().isoformat()
    }
    try:
        collection = db["profiles"]
        collection.insert_one(data_to_save)
        print(f"Successfully saved profile ({data_to_save['user_name']}) to MongoDB.")
        return True
    except Exception as e:
        print(f"Error saving profile to MongoDB: {e}")
        return False

# --- Group Scraping (existing, ensure it's defined before use) ---
def scrape_group_posts(driver, group_url, keyword_search_term, db, num_scrolls=2):
    """Scrapes posts from a specific Facebook group page."""
    print(f"Navigating to group: {group_url}")
    driver.get(group_url)
    random_delay(1.5, 3) # Delay after page navigation
    scraped_posts_data = []
    group_name = None

    try:
        # Wait for the main feed or group posts container to load
        # Also try to get group name here
        group_name_element_xpath = "//h1 | //strong[contains(@class,'x1i10hfl')]" # Common for group titles
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed' or @aria-label='Group feed'] | //div[contains(@class, 'x1hc1fzr')]")),
                EC.presence_of_element_located((By.XPATH, group_name_element_xpath))
            )
        )
        print(f"Successfully navigated to group page: {group_url}")

        # Extract Group Name
        try:
            group_name_el = driver.find_element(By.XPATH, group_name_element_xpath)
            group_name = group_name_el.text.strip()
            print(f"Group Name: {group_name}")
        except NoSuchElementException:
            print("Group name not found on page.")
        except Exception as e:
            print(f"Error extracting group name: {e}")

    except TimeoutException:
        print(f"Timeout waiting for group page to load: {group_url}. Check if the group is public and URL is correct.")
        # driver.save_screenshot(f"group_page_timeout_{group_url.split('/')[-2]}.png")
        return []

    # Scroll down to load more posts
    print(f"Scrolling {num_scrolls} times to load posts...")
    for scroll_num in range(num_scrolls): # Changed to provide scroll number for logging
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scroll {scroll_num + 1}/{num_scrolls} completed.")
        random_delay(2, 4) # Increased delay after scroll for content to load

    # Find post containers - This is highly dependent on Facebook's current HTML structure
    # Common patterns: divs with role="article", or specific complex class structures.
    # The selector below is a guess and will likely need refinement.
    # Using XPath to look for divs that seem to be main post containers.
    # This selector tries to find posts by looking for common text patterns like 'Like', 'Comment', 'Share'
    # or elements that typically hold user content.
    post_elements = driver.find_elements(By.XPATH, "//div[@role='article'] | //div[contains(@class,'x1yztbdb') and contains(@class,'x1n2onr6')] | //div[data-visualcompletion=' μεγαλύτερη ανάρτηση']")

    print(f"Found {len(post_elements)} potential post elements after scrolling.")
    if not post_elements:
        print("No post elements found. Selectors might need updating or group has no visible posts.")
        # driver.save_screenshot(f"no_posts_found_{group_url.split('/')[-2]}.png")
        return []

    for i, post_el in enumerate(post_elements):
        random_delay(0.5, 1.5) # Short delay between processing each post
        print(f"\nProcessing post {i+1}/{len(post_elements)}...")
        post_data = {
            "keyword_search_term": keyword_search_term,
            "group_name": group_name, # Added group name
            "group_url": group_url,
            "post_url": None, # Attempt to get this
            "post_text": None,
            "post_time": None,
            "user_name": None,
            "user_id": None,
            "reactions": {"total": 0}, # Simplified
            "comment_count": 0,
            "scraped_timestamp": datetime.utcnow().isoformat()
        }

        # Extract Post Text
        try:
            # Common selectors for post text: specific class, data-ad-preview, role="paragraph"
            # This selector looks for text directly within the post or within specific known wrappers
            text_element = post_el.find_element(By.XPATH, ".//div[@data-ad-preview='message'] | .//div[contains(@class,'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')] | .//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1n2onr6 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x6s0dn4 xjyslct x9f619 x1ypdohk x78zum5 x1f6kntn xcdnw81 x1i0v60h x3nfvp2 x13vifvy x1q0q8m5 x25902b x1s688f x1h0ha7o')]")
            if text_element: post_data["post_text"] = text_element.text.strip()
            if not post_data["post_text"]: # Fallback for different structures
                text_elements = post_el.find_elements(By.XPATH, ".//div[contains(@class, 'x1iorvi4 x1pi30zi x1l90r2v x1swvt13')]//span[contains(@class, 'x193iq5w')]")
                if text_elements: post_data["post_text"] = " ".join([el.text for el in text_elements if el.text])

        except NoSuchElementException:
            print("Post text not found for this post.")
        except Exception as e:
            print(f"Error extracting post text: {e}")

        # Extract Post Time and URL
        try:
            # Time is often in an <a> tag with a permalink
            time_link_el = post_el.find_element(By.XPATH, ".//a[contains(@href,'/posts/') or contains(@href,'/videos/') or contains(@href,'/photos/') or contains(@href,'?story_fbid=')][@aria-label or @title or contains(@class,'x1i10hfl')]")
            post_data["post_time"] = time_link_el.get_attribute("aria-label") or time_link_el.get_attribute("title") or time_link_el.text # Fallback to text
            post_data["post_url"] = time_link_el.get_attribute("href")
            if not post_data["post_time"]: # Try another common pattern for time
                 time_el = post_el.find_element(By.XPATH, ".//span[contains(@class, 'x4k7w5x') and contains(@class, 'x1emribx')]//span[string-length(text()) > 2]") # Heuristic for time text
                 if time_el: post_data["post_time"] = time_el.text
        except NoSuchElementException:
            print("Post time/URL not found.")
        except Exception as e:
            print(f"Error extracting post time/URL: {e}")

        # Extract User Name and User ID
        try:
            # User link is often an <a> tag with role="link" and contains user's name, href to profile
            user_link_el = post_el.find_element(By.XPATH, ".//strong/ancestor::a[contains(@href,'facebook.com/') and not(contains(@href,'/groups/'))] | .//h3/ancestor::a[contains(@href,'facebook.com/') and not(contains(@href,'/groups/'))] | .//a[contains(@class,'xt0psk2') and contains(@href,'?id=')] | .//a[contains(@class,'x1i10hfl') and contains(@href,'/user/')]")
            post_data["user_name"] = user_link_el.text.strip()
            user_url = user_link_el.get_attribute("href")
            # Try to extract user ID from URL (numeric or vanity)
            match_id = re.search(r"(?:(?:user/|id=)(\d+)|facebook\.com/([^/?]+))", user_url)
            if match_id:
                post_data["user_id"] = match_id.group(1) or match_id.group(2)
        except NoSuchElementException:
            print("User name/ID not found.")
        except Exception as e:
            print(f"Error extracting user name/ID: {e}")

        # Extract Reaction Count (Simplified: Total)
        try:
            # Look for elements that display reaction counts, often with ARIA labels
            # This is very volatile. Example: span with numbers near Like/React buttons.
            # Selector for total reactions (often a span or div with a number)
            reaction_count_el = post_el.find_element(By.XPATH, ".//span[contains(@aria-label,'reaction') and string-length(text()) > 0 and number(translate(text(), 'KMBkmb', '')) = number(translate(text(), 'KMBkmb', ''))] | .//span[contains(@class,'xt0b8zv') and string-length(text()) > 0]")
            # Convert text like "1.2K" to number
            reaction_text = reaction_count_el.text.upper()
            num_part = re.match(r"[\d\.]+", reaction_text)
            if num_part:
                num = float(num_part.group(0))
                if "K" in reaction_text: num *= 1000
                elif "M" in reaction_text: num *= 1000000
                post_data["reactions"]["total"] = int(num)
        except NoSuchElementException:
            print("Reaction count not found.")
        except Exception as e:
            print(f"Error extracting reaction count: {e}")

        # Extract Comment Count
        try:
            # Look for text like "X comments" or "X Shares" to find comment count nearby
            # This is also volatile.
            comment_count_el = post_el.find_element(By.XPATH, ".//div[contains(text(),'comment') or contains(text(),'Comment')] | .//span[contains(text(),'comment') or contains(text(),'Comment')]")
            # Extract number from "X comments"
            match = re.search(r"(\d+)\s*(?:comment| bình luận)", comment_count_el.text, re.IGNORECASE)
            if match:
                post_data["comment_count"] = int(match.group(1))
        except NoSuchElementException:
            print("Comment count not found.")
        except Exception as e:
            print(f"Error extracting comment count: {e}")

        if post_data["post_text"] or post_data["post_url"]: # Only save if we have some content
            print(f"Scraped data: User: {post_data['user_name']}, Text: {post_data['post_text'][:50] if post_data['post_text'] else 'N/A'}...")
            scraped_posts_data.append(post_data)
            if db: # Save to DB if connection is available
                save_post_to_db(db, post_data)
        else:
            print("Skipping post as no significant data (text/URL) was extracted.")

    return scraped_posts_data

def save_post_to_db(db, post_data):
    """Saves a single post data to the MongoDB 'posts' collection."""
    if not db:
        print("Database connection not available. Skipping save.")
        return False
    try:
        collection = db["posts"] # Use a collection named "posts"
        collection.insert_one(post_data)
        print(f"Successfully saved post (URL: {post_data.get('post_url', 'N/A')}) to MongoDB.")
        return True
    except Exception as e:
        print(f"Error saving post to MongoDB: {e}")
        return False

if __name__ == "__main__":
    driver = None
    db_connection = None

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Facebook Scraper CLI")
    parser.add_argument("--user-agent", type=str, help="User agent string to use for the browser.")
    parser.add_argument("--proxy", type=str, help="Proxy server to use (e.g., http://host:port or socks5://host:port).")
    # Potentially add keyword arguments here in future if needed
    # parser.add_argument("--keyword-group", type=str, help="Keyword for group search.")
    # parser.add_argument("--keyword-page", type=str, help="Keyword for page search.")
    # parser.add_argument("--keyword-profile", type=str, help="Keyword for profile search.")

    args = parser.parse_args()
    print(f"Scraper CLI args: User-Agent='{args.user_agent}', Proxy='{args.proxy}'")

    try:
        # Establish MongoDB connection first
        print("Scraper: Initializing MongoDB connection...")
        db_connection = get_db_connection()
        if not db_connection:
            print("Scraper: Failed to connect to MongoDB. Some functionalities will be disabled.")

        driver = initialize_driver(user_agent=args.user_agent, proxy=args.proxy)

        print(f"Scraper: Using Email: {FACEBOOK_EMAIL}, Password: {'*' * len(FACEBOOK_PASSWORD) if FACEBOOK_PASSWORD else 'Not Set'}")
        login_successful = login_to_facebook(driver, FACEBOOK_EMAIL, FACEBOOK_PASSWORD)

        if login_successful:
            print("Scraper: Facebook login process seemingly completed.")
            random_delay(3, 7) # Delay after successful login

            # --- Group Scraping ---
            group_search_keyword = "permaculture design"
            print(f"\nScraper: --- Starting GROUP search for keyword: '{group_search_keyword}' ---")
            group_urls_to_scrape = search_facebook_groups(driver, group_search_keyword)

            if not group_urls_to_scrape:
                print(f"Scraper: No group URLs found for keyword '{group_search_keyword}'.")
            else:
                print(f"\nScraper: Found {len(group_urls_to_scrape)} groups to scrape: {group_urls_to_scrape}")
                for i, group_url in enumerate(group_urls_to_scrape):
                    print(f"\nScraper: --- Navigating to Group {i+1}/{len(group_urls_to_scrape)}: {group_url} ---")
                    random_delay(2, 5) # Delay before navigating to each new group
                    try:
                        scraped_group_posts = scrape_group_posts(driver, group_url, group_search_keyword, db_connection, num_scrolls=1)
                        if scraped_group_posts: print(f"Scraper: Successfully scraped {len(scraped_group_posts)} posts from group {group_url}.")
                        else: print(f"Scraper: No posts were scraped from group {group_url}.")
                    except Exception as e_group_scrape:
                        print(f"Scraper: An error occurred while scraping group {group_url}: {e_group_scrape}")
                        print(f"Scraper: Continuing to next group or section.")

            # --- Page Scraping ---
            page_search_keyword = "sustainable living" # Default or from args.keyword_page
            print(f"\nScraper: --- Starting PAGE search for keyword: '{page_search_keyword}' ---")
            pages_to_scrape = search_facebook_pages(driver, page_search_keyword)

            if not pages_to_scrape:
                print(f"Scraper: No pages found for keyword '{page_search_keyword}'.")
            else:
                print(f"\nScraper: Found {len(pages_to_scrape)} pages to scrape: {pages_to_scrape}")
                for i, page_data in enumerate(pages_to_scrape):
                    page_url = page_data['page_url']
                    page_name = page_data['page_name']
                    print(f"\nScraper: --- Navigating to Page {i+1}/{len(pages_to_scrape)}: {page_name} ({page_url}) ---")
                    random_delay(2, 5) # Delay before navigating to each new page
                    try:
                        scraped_page_posts = scrape_page_posts(driver, page_url, page_name, page_search_keyword, db_connection, num_scrolls=1)
                        if scraped_page_posts: print(f"Scraper: Successfully scraped {len(scraped_page_posts)} posts from page {page_name}.")
                        else: print(f"Scraper: No posts were scraped from page {page_name}.")
                    except Exception as e_page_scrape:
                        print(f"Scraper: An error occurred while scraping page {page_name} ({page_url}): {e_page_scrape}")
                        print(f"Scraper: Continuing to next page or section.")

            # --- Profile "Scraping" (more like profile listing) ---
            profile_search_keyword = "local community leader" # Default or from args.keyword_profile
            print(f"\nScraper: --- Starting PROFILE search for keyword: '{profile_search_keyword}' ---")
            profiles_found = search_facebook_profiles(driver, profile_search_keyword)

            if not profiles_found:
                print(f"Scraper: No profiles found for keyword '{profile_search_keyword}'.")
            else:
                print(f"\nScraper: Found {len(profiles_found)} profiles to potentially save: {profiles_found}")
                for i, profile_data in enumerate(profiles_found):
                    # No specific navigation delay here as we are just saving listed data
                    print(f"\nScraper: --- Saving Profile Info {i+1}/{len(profiles_found)}: {profile_data.get('user_name')} ---")
                    if db_connection:
                        save_profile_data_to_db(db_connection, profile_data, profile_search_keyword)
                    else:
                        print("Scraper: DB connection not available, skipping profile save.")
                    random_delay(0.5,1) # Small delay between DB saves

        else:
            print("Scraper: Facebook login failed or was skipped. Cannot proceed with scraping.")

    except Exception as e:
        print(f"Scraper: An critical error occurred in the main script: {e}")
        # if driver: driver.save_screenshot("critical_error_screenshot.png")
    finally:
        if driver:
            print("Scraper: Closing the browser.")
            driver.quit()
        # Note: MongoDB client connection ideally should be closed if opened,
        # but MongoClient handles pooling and is often kept alive for app lifetime.
        # For a script like this, it might not be explicitly closed here.
        print("Scraper: Script finished.")
