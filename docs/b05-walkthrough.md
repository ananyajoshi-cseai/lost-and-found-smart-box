# B05: understand search results and measure retrieval

## 1. Inspect one search result
Start the backend as in backend/README.md. In /docs, POST /api/search with a query for an item you registered during B04. Results now include safe display attributes and photo_url alongside score, reasons, coverage and related flags. Aashi can build a card directly from this response.

Read coverage_text before interpreting the score. A bottle-only query can score 100 with only 1 of 5 attributes supplied. A related suggestion is a different category and is never proof of ownership. If results is empty, show message; if clarification is non-null, ask the user to clarify the displayed parsed facts.

## 2. Read the labels before measuring
Open backend/tests/fixtures/items.json and queries.json. The latter contains relevant_ids and a rationale, stored separately from the item facts. Notice the two blue Milton bottles, claimed records, explicit exclusions and the unsupported purple color. Do not change aliases or labels after seeing the results just to improve the reported score.

## 3. Run the reproducible evaluation
From backend in PowerShell:

```powershell
.\.venv\Scripts\python.exe evaluation.py --output ../docs/test-results/my-evaluation.json
```

No running server or manual credential setup is required. This command starts a test client with temporary credentials, SQLite database and generated sample photos. It restores your environment and leaves your practice database and uploads untouched. Choose a new output filename for every run; existing reports are not overwritten. Default benchmark: 10 repeats of 12 positive queries over 100 available records, after warm-up.

## 4. Interpret the report
- Top-1: fraction of positive queries whose first card is relevant.
- Top-3: fraction of positive queries with at least one relevant card in the first three.
- Negative false-positive rate: fraction of negative queries returning any card; lower is better.
- Median/p95/max latency: local in-process API response time, not browser/network performance.

Inspect query_runs as well as totals. A query can count as a successful retrieval while still returning extra irrelevant cards. The explicitly broadened case is labelled as related retrieval and is not an exact-category match. Small synthetic results do not establish campus accuracy.

The report records the code commit, whether the checkout was dirty, source/dataset hashes, OS/Python/CPU description, each response and each timing sample. Do not send real claim data into evaluation fixtures.

## 5. Explain one limitation in your viva
Try 'purple bottle'. Purple is outside the authored vocabulary, so the parser can retain only bottle and return other-colored bottles. This is a limitation to report. Any later correction needs a separate development set and tests, preserving this frozen evaluation set.

## 6. Team handoff and next task
Aashi consumes the fields documented in contracts.md; she should review real cards and no-match/clarification states. The B05 report does not certify her frontend. Next is B06: public claim submission, staff-only decisions and atomic audit/state changes.
