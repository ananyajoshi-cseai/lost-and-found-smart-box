# Verification: simplified Finder

This is a new runtime and scope, not the old 86-test FastAPI backend. Python 3.12.14, Windows: dependency consistency passed; 31 tests passed in 1.85 seconds. A real local browser search also displayed three result cards with coverage and per-field points.

The starting parser/ontology/vocabulary/scoring were reused from the original implementation. The public rank wrapper adapts explanations to the proposal's dictionary and preserves coverage. No weights or aliases were tuned on the inherited regression queries. The 40-item UI seed is separate from the 20-item frozen reasoning fixture; the latter's unavailable status spelling is migrated from claimed to returned without changing eligibility.

The JSON store is tested for full report/search/return persistence, corrupt data, invalid fields, duplicate IDs, concurrent additions and interrupted replacement. Streamlit AppTest exercises reporting, score tables, required human confirmation, returning, missing results, ambiguity and visible corrupt-file errors. Initial first-render loading exceeded a 15-second test timeout; the focused rerun passed and cold-start allowance was increased to 45 seconds. No application failure was hidden or scoring logic changed to make the test pass.

Remaining acceptance checks: browser layout, keyboard navigation, narrow-screen behavior, dataset/ontology coverage and a separate final labelled evaluation.

The inherited pure-function regression at clean commit 259a46b5b2630c737c5c1bdab43f78c492059281 recorded 12/12 top-1 and top-3 positive hits and 1/6 negative false positives. Raw results and source hashes are in evaluation/results-v1.json. The known purple-bottle failure is retained. These results are not an independent evaluation of the 40-item UI seed, browser latency or campus accuracy.
