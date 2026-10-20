# Archived backend

Python 3.11+; the initial run was tested on Python 3.12.14. Run commands from `backend` in PowerShell. A virtual environment keeps this project's dependencies separate from other projects.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Do not commit `.venv` or copy it between computers. Activation is unnecessary when using the explicit interpreter below.

Set temporary local demo credentials in each server terminal. These prompts keep values out of source files. The password prompt uses masked input; values exist only in this process environment. `.env.example` lists variable names and is not auto-loaded.

```powershell
$env:DEVICE_KEY = Read-Host 'Choose a local demo device key'
$env:STAFF_USERNAME = Read-Host 'Choose a local demo staff username'
$env:STAFF_PASSWORD = Read-Host 'Choose a local demo staff password' -MaskInput
.\.venv\Scripts\python.exe -m app.database
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

If Windows PowerShell does not support `-MaskInput`, use PowerShell 7 or set a disposable local-only password with `Read-Host`; do not reuse a real password. Credentials must be configured before startup, as required on handbook page 22.

Open http://127.0.0.1:8000/health: expect `{"status":"ok"}`. Explore http://127.0.0.1:8000/docs. Keep the terminal open; Ctrl+C stops the server. Default database is `backend/smartbox.db`; `DATABASE_PATH` overrides it. Initialization is also idempotently performed at startup.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -c "from app.ai.engine import parse; print(parse('navy Milton flask'))"
```

Tests set their own disposable credentials and use temporary databases. They do not modify your demo database. `/api/search` returns no matches until items exist; register an item through `/docs` using the B04 walkthrough. Do not manually put real lost-property records in tests.

Transport errors: 401 = credential problem, 422 = invalid request, 409 = reused ID with different payload. See the full contracts and examples in `../docs/contracts.md`.

References: https://fastapi.tiangolo.com/tutorial/testing/ and https://docs.python.org/3/library/sqlite3.html .

Registration exercise: [B04 walkthrough](../docs/b04-walkthrough.md). `UPLOAD_DIR` optionally overrides the private photo directory. Stop the server before a read-only storage audit with `.\.venv\Scripts\python.exe -m app.services.images`.

B07: [integration and recovery walkthrough](../docs/b07-walkthrough.md) covers /ui/, optional CORS_ORIGINS and offline database/photo backup, verification and fresh-directory restore. Stop the server before backup. The suite includes an actual loopback HTTP test with temporary data.
