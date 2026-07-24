from datetime import datetime
from urllib.parse import quote
import pathlib
import requests
import time 

from matplotlib.dates import relativedelta  

DIRECTORY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
THROTTLE_MESSAGE = "Please limit requests"

def build_url(query: str, start: datetime, end: datetime, maxrecords: int = 250) -> str:
    start_gdelt_time = start.strftime("%Y%m%d%H%M%S")
    end_gdelt_time = end.strftime("%Y%m%d%H%M%S")
    encoded_query = quote(query)

    #Construct the final API endpoint URL
    base_url ="https://api.gdeltproject.org/api/v2/doc/doc?"
    url = f"{base_url}query={encoded_query}&startdatetime={start_gdelt_time}&enddatetime={end_gdelt_time}&maxrecords={maxrecords}&format=json&mode=artlist"

    return url

def fetch_window(url: str) -> list:
    """
    Fetches articles from the GDELT API for a given time window and appends them to the article_list.
    """
    for attempt in range(3):
        response = requests.get(url, timeout = 30)

        if response.text.lstrip().startswith(THROTTLE_MESSAGE):
            print(f"Request throttled. Attempt {attempt + 1} of 3. Retrying in 30 seconds...")
            time.sleep(30)  # Wait for 30 seconds before retrying
            continue  # Retry the request
        
        try:
            data = response.json()
            articles = data.get("articles", [])

        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return []  # Return an empty list even if there's a parsing error
        
        return articles  # Exit the loop if the request was successful
    return []  # Return an empty list if all attempts fail

   






if __name__ == "__main__":
    query = '(heatwave OR heatwaves OR "dust storm" OR hurricane OR "Polar Vortex" OR drought OR Dunkelflaute OR snowfall) ("power grid" OR "electricity grid" OR "blackout" OR "power outage" OR "load shedding" OR "energy demand" OR "electricity demand" OR "peak demand" OR "grid reliability" OR "power failure" OR "power plant" OR "substation" OR "transmission lines" OR "hydroelectric dam" OR "nuclear plant" OR "wind farm" OR "solar array" OR "solar panels" OR  "natural gas" OR "heating oil" OR "electricity prices" OR "energy prices" OR "power supply" OR "generation shortfall")  (Germany OR France OR Spain OR Netherlands OR "United Kingdom") sourcelang:eng'
    start_date = datetime.now() - relativedelta(months=6)
    end_date = datetime.now()
    url = build_url(query, start_date, end_date)
    list_of_articles = fetch_window(url)
    print(url)
    print(f"Number of articles fetched: {len(list_of_articles)}")