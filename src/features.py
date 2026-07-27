"Extract UK time series data Market index per half hour windows from Elexon"
from datetime import datetime
from datetime import datetime, timedelta
import time
import json 
from dateutil.relativedelta import relativedelta
import requests
import pathlib  
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index"
DIRECTORY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw_energy_uk"
ENERGY_CHARTS_URL = "https://api.energy-charts.info/price"

ZONE_TO_REGION = {
    "DE-LU": "Germany",
    "FR": "France",
    "ES": "Spain",
    "NL": "Netherlands",
}


def fetch_zone_energy_charts(zone: str, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Fetches hourly day-ahead prices for one bidding zone from Energy-Charts.
    Returns a dataframe with columns: unix_seconds, price.
    """
    params = {
        "bzn": zone,
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
    }
    for attempt in range(3):
        response = requests.get(ENERGY_CHARTS_URL, params=params, timeout=30)

        if response.status_code not in (200, 429):
            print(f"Error fetching {zone}: {response.status_code} - {response.text[:200]}")
            return pd.DataFrame()

        if response.status_code == 429:
            print(f"Throttled on {zone}. Attempt {attempt + 1} of 3. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        try:
            info = response.json()
            # Parallel arrays: timestamps and prices line up by position
            df = pd.DataFrame({
                "unix_seconds": info["unix_seconds"],
                "price": info["price"],
            })
        except (ValueError, KeyError) as e:
            print(f"Error parsing response for {zone}: {e}")
            return pd.DataFrame()

        return df
    return pd.DataFrame()


def daily_mean_energy_charts(df: pd.DataFrame, region: str) -> pd.DataFrame:
    """
    Aggregates hourly zone prices to a daily mean. Day-ahead auction prices
    have no volume component here, so a plain mean is used (unlike the UK VWAP).
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["unix_seconds"], unit="s", utc=True)
    df["date"] = df["timestamp"].dt.date

    out = df.groupby("date")["price"].mean().reset_index()
    out["region"] = region
    return out
def build_elexon_params(from_date: datetime, to_date: datetime) -> dict:

    #Construct the final API endpoint URL
    params = {
        'from':from_date.strftime('%Y-%m-%dT%H:%MZ'),
        'to':to_date.strftime('%Y-%m-%dT%H:%MZ')
        }

    return params


def fetch_window_elexon(params: dict) -> list:
    """
    Fetches Market Index price data from the Elexon API for a given time window and appends them to the market_index_list.
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
            info = response.json()
            market_data_list = info['data']

        except (ValueError, KeyError) as e:
            print(f"Error parsing JSON response: {e}")
            return []  # Return an empty list even if there's a parsing error
        
        return market_data_list  # Exit the loop if the request was successful
    return []  # Return an empty list if all attempts fail




def fetch_range_elexon(start: datetime, end: datetime,
                out_dir: pathlib.Path = DIRECTORY_PATH) -> None:
    """
    Fetches market index data from the Elexon API week by week.
    """
    
    if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
    current = start

    while current < end:
        end_of_week = current + timedelta(days=7) 
        filename = f"market_index_UK_{current.strftime('%Y%m%d')}_{end_of_week.strftime('%Y%m%d')}.json"
        #Skip to the next week if file already exists
        if (out_dir / filename).exists():
            print(f"File {filename} already exists. Skipping fetch.")

        else:
            params = build_elexon_params(current, end_of_week)
            market_index_list = fetch_window_elexon(params)
            print(f"Fetched {len(market_index_list)} price records for the week starting {current.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}.")

            #Create the directory if it doesn't exist
            # Save the articles to a JSON file
            with open(out_dir / filename, "w") as file:
                json.dump(market_index_list, file, indent=4)
            time.sleep(1)  # Sleep for 1 second to avoid hitting the API too quickly

        current = end_of_week  

def daily_VWAP(df:pd.DataFrame) -> pd.DataFrame:
    '''
    Function to find the daily Volume Weighted Average Price for UK energy market index
    '''
    #Find price x volume 
    df['pv'] = df['price'] * df['volume']
    df["startTime"] = pd.to_datetime(df["startTime"])
    df["date"] = df["startTime"].dt.date

    grouped = df.groupby(['date']).agg(
         total_pv=("pv", "sum"),          # The numerator
         total_volume=("volume", "sum")   
    ).reset_index()

    grouped['daily_VWAP'] = grouped['total_pv'].div(grouped['total_volume'])

    out = grouped[['date', 'daily_VWAP']].rename(columns={'daily_VWAP': 'price'})
    out['region'] = 'UK'

    return out

    

if __name__ == "__main__":
    start = datetime.now() - relativedelta(months=12)
    end = datetime.now()

    # UK: Elexon market index, volume-weighted
    fetch_range_elexon(start, end)
    uk_raw = pd.concat([pd.read_json(f) for f in sorted(DIRECTORY_PATH.glob("*.json"))], ignore_index=True)
    frames = [daily_VWAP(uk_raw)]

    # Other markets: Energy-Charts day-ahead, plain daily mean
    for zone, region in ZONE_TO_REGION.items():
        zone_df = fetch_zone_energy_charts(zone, start, end)
        if zone_df.empty:
            print(f"WARNING: no data for {region} ({zone})")
            continue
        frames.append(daily_mean_energy_charts(zone_df, region))
        time.sleep(1)

    prices = pd.concat(frames, ignore_index=True)
    prices.to_csv(pathlib.Path(__file__).resolve().parents[1] / "data" / "processed" / "prices.csv", index=False)

    print(prices.groupby("region")["price"].describe())





