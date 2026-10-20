# Run the simplified Finder

Python 3.12 is the tested target. Open a terminal in this `finder` folder. The old backend virtual environment is separate; do not use it here.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

The prepared local checkout already has the new environment. Open http://127.0.0.1:8501. Keep the terminal open; Ctrl+C stops the app. No credentials, database service or device is needed. The Streamlit config binds to loopback and disables usage telemetry; run from this folder so it is loaded. Do not expose this unauthenticated classroom demo publicly.

## Try the full flow

1. Search for `navy Milton flask`. Check Understood before pressing Find matches. Read coverage and the points table, not just the total.
2. Search `bottle not blue`, then `red blue bottle`: inspect the exclusion and clarification behavior.
3. Open Report Found Item. Choose canonical facts, save, and note the new item ID.
4. Search those facts. Several identical-looking items may appear; sorting is by score and then ID, with only the top three shown. Use Staff to find your saved ID if it is not among those three.
5. Open Staff — mark returned. Choose the ID, verify the displayed facts and tick the human-verification checkbox. Mark returned.
6. Search again; that returned ID is excluded. Restart the app and verify that the return persisted.

Staff is a demo control, not an authenticated staff account. No claim, ownership proof or contact information is collected. Scores are text agreement, never ownership probability.

## Data and recovery

`data/items.seed.json` contains 40 synthetic starter records, including deliberate same-description pairs with different IDs. They reuse the earlier 20-item fixture; Anika should review realism and extend coverage rather than treating these as independent observations. The current vocabulary contains seven leaf categories plus three parent nodes; expanding to the proposal's approximately twelve categories remains Anika's task.

On first read/write, a missing `runtime/items.json` is initialized from the seed. Subsequent reports and returns affect only that ignored runtime file. An existing empty file/list is not repopulated; malformed data produces a visible error and is never silently reset. JSON updates use a lock and temporary-file replacement to avoid partial writes and lost updates between local sessions. This is small local storage, not a multi-user hosted database.

To back up, stop the app and copy `runtime/items.json` to a private folder. To restore, stop the app, retain the current file as a separate backup, then copy the desired valid JSON file to `runtime/items.json`. To start a fresh demo without deleting data, set `FINDER_DATA_PATH` to a new filename before launch. The seed initializes that new path. Never commit real lost-property records.

## Tests and regression evidence

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe evaluate.py --output ../work/finder-evaluation.json
```

Tests use temporary JSON files. The evaluator calls pure functions against the inherited 20-item/18-query frozen regression set; it does not read or change runtime data. Aashi should create a separate final labelled evaluation for the agreed 40-item dataset. Do not tune vocabulary or weights against final test queries. The old HTTP latency figures and 86-test backend total are not measurements of this app.

The GUI uses Streamlit [page navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation) and its [AppTest framework](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) for simulated interface checks. Browser layout and team rehearsal still require human review.

Your next learning step: [Ananya's reasoning exercise](ANANYA-NEXT.md). Team branch/review instructions and live task links are in [CONTRIBUTING.md](../CONTRIBUTING.md).
