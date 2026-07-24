"""ingest.py - see PROJECT_PLAN.md for the spec. Write this yourself."""
from datetime import datetime
from urllib.parse import quote
import pathlib

from matplotlib.dates import relativedelta  

DIRECTORY_PATH = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"

def build_url(query: str, start: datetime, end: datetime, maxrecords: int = 250) -> str:
    start_gdelt_time = start.strftime("%Y%m%d%H%M%S")
    end_gdelt_time = end.strftime("%Y%m%d%H%M%S")
    encoded_query = quote(query)

    #Construct the final API endpoint URL
    base_url ="https://api.gdeltproject.org/api/v2/doc/doc?"
    url = f"{base_url}query={encoded_query}&startdatetime={start_gdelt_time}&enddatetime={end_gdelt_time}&maxrecords={maxrecords}&format=json&mode=artlist"

    return url


if __name__ == "__main__":
    query = '(heatwave OR heatwaves OR "dust storm" OR hurricane OR "Polar Vortex" OR drought OR Dunkelflaute OR snowfall) ("power grid" OR "electricity grid" OR "blackout" OR "power outage" OR "load shedding" OR "energy demand" OR "electricity demand" OR "peak demand" OR "grid reliability" OR "power failure" OR "power plant" OR "substation" OR "transmission lines" OR "hydroelectric dam" OR "nuclear plant" OR "wind farm" OR "solar array" OR "solar panels" OR  "natural gas" OR "heating oil" OR "electricity prices" OR "energy prices" OR "power supply" OR "generation shortfall")  (Germany OR France OR Spain OR Netherlands OR "United Kingdom") sourcelang:eng'
    start_date = datetime.now() - relativedelta(months=6)
    end_date = datetime.now()
    url = build_url(query, start_date, end_date)
    print(url)