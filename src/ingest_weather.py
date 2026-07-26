"""
Second ingestion pass: weather-focused query.

The main pull (ingest.py) uses an energy-centric query, so real weather events
are rare in it (13 in 279 articles). That is too few to measure per-class
accuracy for event_type, so this pass collects weather headlines specifically.

Kept as a separate dataset in data/raw_weather/. The random sample from the
main pull stays the unbiased estimate of the live distribution; this one is
only used to measure event classification where the classes are rare.
"""
import pathlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

from ingest import fetch_range

WEATHER_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw_weather"

# No energy term is required here. Requiring both a weather word and an energy
# word in the same headline returned almost nothing (total=2 when tested), and
# the point of this set is to measure event_type, not energy relevance.
QUERY = (
    '(heatwave OR "cold snap" OR storm OR blizzard OR flood OR flooding '
    'OR drought OR freeze OR snow OR gale OR hurricane OR cyclone '
    'OR "extreme heat" OR "record heat" OR "record temperatures")'
)

if __name__ == "__main__":
    fetch_range(
        QUERY,
        datetime.now() - relativedelta(months=12),
        datetime.now(),
        page_size=100,
        out_dir=WEATHER_DIR,
    )
