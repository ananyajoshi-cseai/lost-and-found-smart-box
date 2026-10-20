# Campus Lost & Found Finder

A local lost-and-found app built with Python, Streamlit and JSON. It uses keyword matching, explicit rules, a category tree and weighted scoring. No machine learning, external inference service or hardware is required.

## Run

Python 3.12 is the tested version. From the repository root:

```powershell
cd finder
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open http://127.0.0.1:8501. Keep the terminal open; Ctrl+C stops the app. On macOS/Linux, use `python3` to create the environment and `.venv/bin/python` for the remaining commands. Run Streamlit from `finder/` so its local configuration is loaded.

## Features

- **Search:** describe an item, inspect the interpreted facts and view up to three matches with score explanations.
- **Report Found Item:** save an item using the available category, color, brand, location and mark options.
- **Mark Returned:** confirm an item's return; it is then excluded from future search results.

Example queries: `navy Milton flask`, `bottle not blue`, `red blue bottle`. Synonyms map to canonical values, exclusions filter candidates, and conflicting values request clarification. Optional related-category search uses BFS to depth two when no eligible exact-category item exists.

## Matching

Weights: category **40**, color **25**, brand **15**, location **10**, mark **10**.

`score = 100 × matching supplied weight / total supplied positive weight`

Only supplied positive fields count. Scores below 50 are excluded; ties use item ID. Coverage shows how many of the five attributes were supplied. A category-only query can score 100 with coverage 1/5. Scores indicate text agreement, not ownership probability; returns require human verification.

The vocabulary is manually defined. Unknown words and misspellings are ignored, and negation supports only immediate `not`, `no` or `without`. For example, use `bottle not blue` instead of `not a blue bottle`. The Staff page has no authentication and is intended for a supervised local demo.

## Data

`finder/data/items.seed.json` contains 40 synthetic starter records, including similar-looking items. The first use creates `finder/runtime/items.json`; additions and returns persist there. Runtime data is ignored by Git. Invalid files produce an error rather than being reset.

Stop the app before copying the runtime JSON for backup or restoring a saved copy. Set `FINDER_DATA_PATH` to a different filename for an isolated demo. No photos, contacts or private ownership details are collected.

## Tests and evaluation

From `finder/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe evaluate.py --output runtime/evaluation.json
```

Tests use temporary files. The evaluator uses a fixed 20-item/18-query regression dataset, separate from the 40-item app seed, and reports top-1, top-3 and negative false positives. Choose a new output filename for each run. These synthetic results are not campus accuracy; a separate final evaluation is still required.

## Code layout

- `finder/streamlit_app.py` and `finder/views/`: the three app pages.
- `finder/finder_core/`: parser, vocabulary, BFS, ranking and JSON storage.
- `finder/data/`: synthetic starter items.
- `finder/tests/`: reasoning, storage and interface tests.
- `finder/evaluate.py` and `finder/evaluation/`: regression runner and input fixtures.
- `finder/requirements.txt`, `finder/.streamlit/` and `.github/workflows/`: dependencies, local settings and automated tests.
