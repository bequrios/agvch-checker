import pandas as pd
import requests
import json
from datetime import datetime, date
from pathlib import Path

# Official data from the BFS API
def fetch_official_data():
    # Read API data into dataframe
    official = pd.read_csv(f"https://www.agvchapp.bfs.admin.ch/api/communes/snapshot?date={datetime.now().strftime('%d-%m-%Y')}")

    # Only use communes (Level 3)
    official = official[official["Level"] == 3]

    # Convert Parent and Inscription columns to nullable integer type
    official.Parent = official.Parent.astype("Int64")
    official.Inscription = official.Inscription.astype("Int64")

    return official

# Wikidata Data
def wikidata_missing_bfs_codes(official):

    # Endpoint URL
    url = "https://query.wikidata.org/sparql"

    # Query string to get BFS codes from Wikidata
    query = """
    SELECT * WHERE {
        ?muni wdt:P771 ?bfs_code.
    }
    """
    # Make the request to the Wikidata SPARQL endpoint
    response = requests.get(url, params={'query': query, 'format': 'json'})
    data = response.json()
    data = pd.json_normalize(data['results']['bindings'])

    # Convert BFS codes to int
    data["bfs_code.value"] = data["bfs_code.value"].astype("Int64")

    # Create a DataFrame with missing BFS codes
    missing = official[~official["BfsCode"].isin(data["bfs_code.value"])]

    # Ensure missing values are handled correctly
    missing = missing.replace({pd.NA: None, float('nan'): None})

    return missing[["HistoricalCode", "BfsCode", "ValidFrom", "Name"]]

# LINDAS missing versions
def lindas_missing_versions(official):
    # Endpoint URL
    url = "https://ld.admin.ch/query"

    headers = {
        "Accept": "application/sparql-results+json"
    }

    # Query string to get BFS codes from Wikidata
    query = """
    PREFIX schema: <http://schema.org/>
    PREFIX vl: <https://version.link/>
    SELECT ?identifier WHERE {
    ?version a vl:Version;
            vl:inVersionedIdentitySet <https://ld.admin.ch/fso/register>;
            schema:identifier ?identifier.
    }
    """
    # Make the request to the Wikidata SPARQL endpoint
    response = requests.get(url, params={'query': query}, headers=headers)
    data = response.json()
    data = pd.json_normalize(data['results']['bindings'])

    # Convert BFS codes to int
    data["identifier.value"] = data["identifier.value"].astype("Int64")

    # Create a DataFrame with missing BFS codes
    missing = official[~official["HistoricalCode"].isin(data["identifier.value"])]

    # Ensure missing values are handled correctly
    missing = missing.replace({pd.NA: None, float('nan'): None})

    return missing[["HistoricalCode", "BfsCode", "ValidFrom", "Name"]]


# String for today's date
today_str = date.today().isoformat()  # e.g., '2025-08-04'

# Path to JSON log file
json_path = Path("data.json")

# Load existing data or start fresh
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
else:
    all_data = {}

official = fetch_official_data()

# Add or overwrite today's data
all_data[today_str] = {
    "wikidata_missing_bfs_codes": wikidata_missing_bfs_codes(official).to_dict(orient="records"),
    "lindas_missing_versions": lindas_missing_versions(official).to_dict(orient="records")
}

# Order the data by date
all_data = dict(sorted(all_data.items(), key=lambda item: datetime.strptime(item[0], "%Y-%m-%d"), reverse=True))

# Save updated data
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)