from datetime import datetime, timedelta
import os
import pathlib
import requests
import time 
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv 

load_dotenv()

API_KEY = os.getenv("GUARDIAN_API_KEY")
DIRECTORY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
BASE_URL = "https://content.guardianapis.com/search"

def build_guardian_params(query: str, start: datetime, end: datetime, page_size: int = 50) -> dict:
    start_time = start.strftime("%Y-%m-%d")
    end_time = end.strftime("%Y-%m-%d")

    #Construct the final API endpoint URL
    params = {
        "q": query,
        "query-fields": "headline",
        "from-date": start_time,
        "to-date": end_time,
        "page-size": page_size,
        "api-key": API_KEY  
    }

    return params

def fetch_window(params: dict) -> list:
    """
    Fetches articles from the Guardian API for a given time window and appends them to the article_list.
    """
    for attempt in range(3):
        response = requests.get(BASE_URL, params=params, timeout = 30)

        if response.status_code not in (200, 429):  # Check for successful response or rate limiting   
            print(f"Error fetching data: {response.status_code} - {response.text}")
            return []  # Return an empty list if there's an error other than rate limiting

        if response.status_code == 429:  # Check for rate limiting
            print(f"Request throttled. Attempt {attempt + 1} of 3. Retrying in 30 seconds...")
            time.sleep(30)  # Wait for 30 seconds before retrying
            continue  # Retry the request
        
        try:
            data = response.json()
            articles = data["response"]["results"]

        except (ValueError, KeyError) as e:
            print(f"Error parsing JSON response: {e}")
            return []  # Return an empty list even if there's a parsing error
        
        return articles  # Exit the loop if the request was successful
    return []  # Return an empty list if all attempts fail

def fetch_range(query: str, start: datetime, end: datetime, page_size: int = 50,
                out_dir: pathlib.Path = DIRECTORY_PATH) -> None:
    """
    Fetches articles from the Guardian API week by week.
    out_dir lets a second pull (e.g. a weather-focused query) write to its own
    folder so the weekly filenames do not collide with the main pull.
    """
    if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
    current = start

    while current < end:
        end_of_week = current + timedelta(days=7) 
        filename = f"articles_{current.strftime('%Y%m%d')}_{end_of_week.strftime('%Y%m%d')}.json"
        #Skip to the next week if file already exists
        if (out_dir / filename).exists():
            print(f"File {filename} already exists. Skipping fetch.")

        else:
            params = build_guardian_params(query, current, end_of_week, page_size)
            list_of_articles = fetch_window(params)
            print(f"Fetched {len(list_of_articles)} articles for the week starting {current.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}.")

            #Create the directory if it doesn't exist
            # Save the articles to a JSON file
            with open(out_dir / filename, "w") as file:
                json.dump(list_of_articles, file, indent=4)
            time.sleep(1)  # Sleep for 1 second to avoid hitting the API too quickly

        current = end_of_week 



if __name__ == "__main__":
    query = '(electricity OR "power prices" OR "energy prices" OR blackout OR "power outage" OR "power cut" OR "National Grid" OR "gas supply" OR "wind" OR "solar" OR "energy crisis" OR "power grid" OR "wind power" OR "solar power" OR "energy bills")'
    fetch_range(query, datetime.now() - relativedelta(months=12), datetime.now(), page_size=100)
