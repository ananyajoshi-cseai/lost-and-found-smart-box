# Verification: simplified Finder

This is a new runtime and scope, not the old 86-test FastAPI backend. Measurements below will be recorded after the simplified suite and pure-Python regression run complete.

The starting parser/ontology/vocabulary/scoring were reused from the original implementation. The public rank wrapper adapts explanations to the proposal's dictionary and preserves coverage. No weights or aliases were tuned on the inherited regression queries. The 40-item UI seed is separate from the 20-item frozen reasoning fixture; the latter's unavailable status spelling is migrated from claimed to returned without changing eligibility.

The JSON store is tested for full report/search/return persistence, corrupt data, invalid fields, duplicate IDs, concurrent additions and interrupted replacement. Streamlit AppTest exercises reporting, score tables, required human confirmation, returning, missing results, ambiguity and visible corrupt-file errors. Initial first-render loading exceeded a 15-second test timeout; the focused rerun passed and cold-start allowance was increased to 45 seconds. No application failure was hidden or scoring logic changed to make the test pass.

Remaining human checks: real browser layout/keyboard/narrow screen; all three teammates launch and explain their modules; Anika reviews dataset/ontology extensions; Aashi authors a separate final evaluation. This initial scaffold is not evidence that teammates have completed their assigned work or that the course has accepted dropping IoT.
