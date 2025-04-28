import csv
import requests
import os
import glob
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime, timezone

SPARQL_ENDPOINT = "https://ld.admin.ch/query"
SPARQL_QUERY = """
PREFIX schema: <http://schema.org/>
PREFIX vl: <https://version.link/>
SELECT ?identifier WHERE {
  ?version a vl:Version;
           vl:inVersionedIdentitySet <https://ld.admin.ch/fso/register>;
           schema:identifier ?identifier.
}
"""

def build_csv_url():
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%d-%m-%Y")  # format: DD-MM-YYYY
    return f"https://www.agvchapp.bfs.admin.ch/api/communes/snapshot?date={date_str}"

def fetch_csv_historical_codes():
    response = requests.get(build_csv_url())
    response.raise_for_status()
    lines = response.text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

def fetch_identifiers_from_rdf():
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(SPARQL_QUERY)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return set(r['identifier']['value'] for r in results["results"]["bindings"])

def write_missing_rows(missing_rows):
    
    # Delete old missing.csv files
    for filename in glob.glob("*_missing.csv"):
        os.remove(filename)

    # Build today's filename
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_filename = f"{today_str}_missing.csv"
    
    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        if missing_rows:
            missing_sorted = sorted(missing_rows, key=lambda x: int(x['HistoricalCode']))
            writer = csv.DictWriter(f, fieldnames=missing_rows[0].keys())
            writer.writeheader()
            writer.writerows(missing_sorted)
        else:
            f.write("No missing rows found.\n")

def main():
    print("Fetching CSV...")
    rows = fetch_csv_historical_codes()
    csv_codes = {row["HistoricalCode"] for row in rows if row["HistoricalCode"]}

    print("Fetching RDF identifiers...")
    rdf_codes = fetch_identifiers_from_rdf()

    print("Comparing...")
    missing_rows = [
    row for row in rows
    if row["HistoricalCode"] not in rdf_codes and int(row["Level"]) == 3]
    print(f"Found {len(missing_rows)} missing codes.")

    write_missing_rows(missing_rows)

if __name__ == "__main__":
    main()
