# AGVCH Checker

This tool does some daily checks (`checker.py`) via GitHub actions to find missing and wrong data in LINDAS and Wikidata. The source of truth thereby is the official [AGVCH application](https://www.agvchapp.bfs.admin.ch).

The results of the test are written to `data.json` for each day. This will allow some longitudinal analysis afterwards.
