# AGVCH Checker

This tool does some daily checks (`checker.ipynb`) via GitHub actions to find missing and wrong data in LINDAS and Wikidata. The source of truth thereby is the official [AGVCH application](https://www.agvchapp.bfs.admin.ch).

Each day, two files are generated:

## Tabular Data

Tabular data is written to `current_munies/YYYY-MM-DD.csv`. This file is a merge between the official AGVCH application data and Wikidata data. The following columns are in the file:

- BfsCode: BFS number from AGVCH
- Name: Official name from AGVCH
- q: Identifier from Wikidata
- name: Name from Wikidata ([P1448](https://www.wikidata.org/wiki/Property:P1448) - official name)
- lang: Language tag for `name` ('und' means 'undefined')
- bfs: BFS number from Wikidata
- bfsInt: BFS number as integer (`bfs` often given in the form `"0001"`)
- _merge: Result of the merge operation (can be `both`, `official_only` and `wikidata_only`)
- _nameOk: Boolean for correct `name`
- _bfsOk: Boolean for correct `bfs` number

## JSON Data

The JSON data is written to `summaries/YYYY-MM-DD.json`. This file contains summarized results of the check. In addition it contains the missing municipality versions in LINDAS. The following fields are in the file:

- _merge: Number of all different merge results
- _nameOk: Number of municipalities with correct names
- _bfsOk: Number of municipalities with correct BFS numbers
- _bfsIntUnique: Boolean whether bfsInt are all unique
- _BfsCodeUnique: Boolean whether BfsCode are all unique
- _bfsIntNonUniqueValues: The non-unique values of bfsInt
- _BfsCodeNonUniqueValues: The non-unique values of BfsCode

- missing_lindas_versions: A list of missing municipality versions that are not present yet in LINDAS

## Explanation of Different Errors

- `wikidata_only`: The municipality is only present in Wikidata, but not in the official AGVCH application. --> Future municipalities that are already present in Wikidata or deprecated ones that have not the https://www.wikidata.org/wiki/Q70208 class removed
- `_nameOk: False`: Wrong name in Wikidata
- `_bfsOk: False`: Wrong format of BFS number in Wikidata (https://www.wikidata.org/wiki/Property:P771), e.g. 000x instead of just x
- if there are multiple matches (`_bfsIntUnique: False`), it could be that the BFS number is assigned more than once in Wikidata, but most probable there are multiple offical names in Wikidata resulting in more than one result that matches.
