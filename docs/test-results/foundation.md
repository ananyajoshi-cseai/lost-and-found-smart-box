# Verified foundation checkpoint

Executed 18 October 2026 on Windows, Python 3.12.14, pytest 9.1.1.

Command: `.venv/Scripts/python.exe -m pytest -q` with an isolated temporary test directory.
Result: **25 passed, 1 warning in 0.95s**.

Covers deterministic aliases, negation, ambiguity, unknown words, missing values, score arithmetic, coverage, tie order, top-three limit, availability, BFS distance and broadening, /health, authenticated event intake and retry/conflict statuses, validation, pending events, persistence across app restart, FK/unique constraints, database-backed search, private-field exclusion, one approved claim constraint and append-only audit.

Warning: installed Starlette reports that its httpx TestClient adapter is deprecated in favor of httpx2. The handbook specifies httpx; the pinned dependency set passes. No warning was suppressed. Revisit adapter choice on a deliberate dependency upgrade.

The restricted shell stalled in the HTTP test client; the complete suite passed outside that restriction. Tests never used real user data. This is not a Wokwi, physical hardware, full registration/claim-route, or retrieval-accuracy result. CI status is separate from this local result.
