from pydantic import BaseModel, ValidationError
from anthropic import Anthropic 
from typing import Literal
from dotenv import load_dotenv
import os
import json
import pandas as pd
import pathlib
import time 

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


SYSTEM_PROMPT = """You are a helpful assistant that extracts structured information from news headlines.
You will be given a news headline and your task is to extract the following information:
1. Event Type: Identify the type of weather event mentioned in the headline. The possible event
    types are: "heatwave", "cold", "storm", "flood", "drought", or "none" if no specific weather event is mentioned.    
2. Region: which market the headline is about, labelled per the following rules:
Your output should be a JSON object with the following structure:
{
    "event_type": "<event_type>",
    "region": "<region>"
}
Make sure to only output the JSON object and nothing else. Do not include any explanations or additional text. The JSON object should be valid and parsable.
Reply with only a JSON object, no markdown fences, no explanation, exactly this shape: {"event_type": "storm", "region": "UK"}    

    ## Two columns : `region` and `event_type`

    ### Part 1 : `region`
    - The Guardian is a UK-based paper with global coverage
    - We extracted 5 of the biggest economies in europe which serve as our target markets: UK, Germany, France, Spain, Netherlands

    - **RULE 1**:  (`UK`, `Germany`, `France`, `Spain`, `Netherlands`) as labels

    - **RULE 2**: Label "Europe" as `Europe`

    - **RULE 3**: Label non–target european countries (not UK, Germany, France, Spain, Netherlands) or non-european countries as `other` to avoid confounding results of our targeted study.
    Examples: 
    Russia -> `other`
    US -> `other`

- **RULE 4**: Britain / Great Britain / England / Scotland / Wales / GB -> label `UK`. Holland -> `Netherlands`.

- **RULE 5**: **When** no country is named and the headline is about domestic life (bills, households, consumer advice and shopping, the grid, regulators, politics) -> `UK`. When no country is named and the story has no national subject at all (science studies, global markets, general explainers) -> `other`..

Example: "Energy bills to rise again in April" -> UK. 

Example: "Changes in solar energy fuelled high speed evolutionary changes, study suggests" -> `other`.

Example: "Energy bills to rise again in April" -> `UK`

- **RULE 6**: When a nationality adjective appears instead of a country name, label the matching country: British / English / Scottish / Welsh -> UK, French -> France, German -> Germany, Spanish -> Spain, Dutch -> Netherlands, European -> Europe.

Example: "British households face record winter bills" -> UK

- **RULE 7**: When a headline names more than one region, label the widest one that covers them.
If a target country and a bloc appear together, label Europe. Example: "Iran war threatens to delay large offshore wind projects in EU and UK" -> Europe.
If two or more target countries appear with no bloc, also label Europe. Example: "France and Germany agree emergency power sharing" -> Europe.
If a target country appears alongside a non-target country, label the target country, since that is the market we study. Example: "UK and China sign nuclear deal" -> UK.

### Part 2 : `event_type`
- **RULE 1**:  **When** the headline reports weather that happened or is happening (a heatwave, a storm, record sunshine), label the event type. **When** weather words appear only as industry/policy topics (wind farms, solar subsidies, "*wind power auction*"), **label** none. 
Value Types: {`heatwave`, `cold`, `storm`, `flood`, `drought`, `none`}
`cold`: cold snap, freeze, frost, ice, icy conditions, snow, blizzard, big freeze
`storm`: storm, gale, high winds, cyclone, hurricane, typhoon, tornado
`flood`: flooding, floods, deluge, burst rivers
`heatwave`: heatwave, extreme heat, record temperatures, scorcher
`drought`: drought, water shortage, hosepipe ban
`none`: none of the above

Example: "*Europe's heatwave drives electricity prices*" -> heatwave. Example: "*Record wind power auction proves doubters wrong*" -> none.

- **RULE 2**: **When** the headline asserts that a real weather event is happening or is
  forecast, **label** that event, whatever else the article is about. **When** the weather
  word is a name, a metaphor, or a policy term, **label** `none`. 
  **When** a season named without a specific event (this winter, summer bills) is not an event -> `none`." 

Example: "Not cool: the air conditioning scams offering fake deals in the heatwave" -> `heatwave`
(the story is about fraud, but a real UK heatwave is happening)
Example: "Raise £12bn in budget by extending income tax thresholds freeze, says thinktank" -> `none`
(freeze is fiscal policy, not weather)
Example: "20 things to wear to stay warm this winter" -> seasonal, no event asserted -> `none`
"New year revellers told to wrap up warm with snow expected across UK" -> specific forecast asserted -> `cold`

- **RULE 3**: The event must be current or forecast. **When** the headline only refers back to
  a past event, **label** `none`. A flood that happened months ago does not move prices today.

Example: "Not cool: the air conditioning scams offering fake deals in the heatwave" -> `heatwave`
(happening now)
Example: "UK rejects visa for girl left destitute in Jamaica by Hurricane Melissa" -> `none`
(the hurricane is over; the story is about a visa decision)

Reply with only the raw JSON object. No markdown fences
"""


class Extraction(BaseModel):
    event_type: Literal["heatwave", "cold", "storm", "flood", "drought", "none"]
    region: Literal["UK", "Germany", "France", "Spain", "Netherlands", "Europe", "other"]


def extract_headline(title: str) -> Extraction:
    """
    Extracts structured information from a news headline using the Anthropic API.
    
    Args:
        title (str): The news headline to extract information from.
        
    Returns:
        Extraction: A Pydantic model containing the extracted event type and region.
    """
    response = client.messages.create(
        model='claude-haiku-4-5',
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Headline: '{title}'"},
        ]
    )

    text = response.content[0].text.strip()
    
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    
    parsed = json.loads(text)
    result = Extraction(**parsed)
    
    return result

def extract_batch(df, cache_path) -> dict:
    """
    Extracts structured information from a batch of news headlines and caches the results.
    
    Args:
        df (pd.DataFrame): DataFrame containing the news headlines with a 'webTitle' column.
        cache_path (str): Path to the cache file for storing extracted results.
    """
    if not os.path.exists(cache_path):
        cache = {}
    else:
        with open(cache_path, 'r') as f:
            cache = json.load(f)
    for index, row in df.iterrows():
        title = row['webTitle']
        url = row['webUrl']
        if url in cache:
            continue
        try:
            extraction = extract_headline(title)
            cache[url] = extraction.model_dump()

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Failed on '{title}': {e}")
            cache[row['webUrl']] = {"error": str(e)}

        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)

        time.sleep(0.5)

        print(f"{index + 1}/{len(df)} done")

    return cache 


if __name__ == "__main__":
    base = pathlib.Path(__file__).resolve().parents[1]
    gold = pd.read_csv(base / "data" / "labeled" / "gold.csv")
    enriched = pd.read_csv(base / "data" / "labeled" / "gold_enriched.csv")
    gold["source"] = "random"
    enriched["source"] = "enriched"
    both = pd.concat([gold, enriched], ignore_index=True)
    extract_batch(both, base / "data" / "processed" / "extractions.json")
