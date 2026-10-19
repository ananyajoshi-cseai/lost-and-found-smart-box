# B07: backend integration and recovery

## What is ready

The backend now serves Aashi's frontend at `/ui/`, supports optional restricted local CORS, and provides offline database-plus-photo backup and restore commands. Existing API paths and payloads are unchanged. The committed replay script reports failures without replacing the saved event ID or automatically retrying.

As of this checkpoint, the frontend and hardware branches contain scaffolding, not a finished browser client or Wokwi circuit. `/ui` redirects to `/ui/`; without `frontend/index.html`, it returns 503 with an explanation. This is expected. Use `/docs` for backend exercises meanwhile.

## 1. Run the integration test

From `backend`, with the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Local result: **86 passed in 11.05 seconds**, with one existing Starlette/httpx deprecation warning. The integration test starts a real server on a temporary loopback port and invokes the committed replay script over HTTP. It verifies new/duplicate events, wrong credentials, conflicting IDs, registration, search, competing claims, staff approval, hidden claimed photos, and an offline backup restored into a fresh location. It then restarts against the restored copy and checks claims, audit, available photos, search and health. All records and images are synthetic and temporary; your demo database is untouched.

Fixture HTML tests verify static hosting; they do not establish that Aashi's UI works. Synthetic serial JSON does not establish that Anika's Wokwi trigger works.

## 2. Host the reviewed frontend

Once Aashi's reviewed files are merged into `frontend/`, launch the backend as described in its README and visit `http://127.0.0.1:8000/ui/`. Use relative asset paths and API paths beginning `/api/`. Only `frontend/` is mounted; keep credentials, databases, backup bundles and private files out of that directory.

Same-origin hosting requires no CORS configuration. If Aashi uses a separate development server, set this before launching the backend:

```powershell
$env:CORS_ORIGINS = 'http://localhost:5500,http://127.0.0.1:5500'
```

Only those exact origins are allowed; wildcard or other origins reject startup. Leave the variable unset or empty for same-origin work. CORS does not replace staff authentication. See [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/) and [CORS](https://fastapi.tiangolo.com/tutorial/cors/).

## 3. Make a recoverable copy of your local demo

First finish requests and stop the server with Ctrl+C. Run the following from `backend`. These examples assume the default `smartbox.db` and `uploads` paths; if you set `DATABASE_PATH` or `UPLOAD_DIR`, supply those actual source paths instead.

```powershell
New-Item -ItemType Directory -Force backups, restores | Out-Null
$checkpoint = Get-Date -Format 'yyyyMMdd-HHmmss'
$bundle = Join-Path (Get-Location) "backups\$checkpoint"
$recovered = Join-Path (Get-Location) "restores\$checkpoint"
.\.venv\Scripts\python.exe -m app.recovery backup --database smartbox.db --uploads uploads --destination $bundle --server-stopped
```

Continue only if the command exits successfully and the bundle contains `manifest.json`. `--server-stopped` is your acknowledgement; it does not stop or detect a running server. SQLite's backup API copies the database, while the stopped server keeps database references and photos consistent. The manifest records referenced photo files, row counts and SHA-256 checksums. Unreferenced/orphan photos are not copied. See [Python SQLite backup](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).

```powershell
.\.venv\Scripts\python.exe -m app.recovery verify $bundle
```

Continue only after verification succeeds. Restore into the new directory:

```powershell
.\.venv\Scripts\python.exe -m app.recovery restore $bundle --destination $recovered
```

Continue only if restore succeeds and `RESTORE_COMPLETE.json` exists. Existing destinations are refused. A failed operation may leave an incomplete directory; do not start the app against it. Choose a new destination for the next attempt. Neither command replaces your active database or photos.

With your demo credentials still configured, point a stopped backend to the verified copy:

```powershell
$env:DATABASE_PATH = Join-Path $recovered 'smartbox.db'
$env:UPLOAD_DIR = Join-Path $recovered 'uploads'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Check `/health`, available item photos/search, and the staff claims/audit list against the original checkpoint. To return to the original default paths, stop the server, remove these two environment overrides, and relaunch. If you previously used custom paths, restore those values instead.

```powershell
Remove-Item Env:DATABASE_PATH, Env:UPLOAD_DIR -ErrorAction SilentlyContinue
```

Keep bundles private: they contain contact details, evidence, private marks and photos. Checksums detect accidental corruption, not authenticity or encryption. These tools are for trusted local backups. The ignored `backups/` and `restores/` directories keep the exercise out of Git; do not publish or place them inside `frontend/`.

## 4. Complete the team acceptance gate

Issue #7 stays open until actual team integration is demonstrated:

- [x] Backend routes, static hosting and restricted CORS tested.
- [x] Actual replay script tested over loopback HTTP, including duplicate and error cases.
- [x] Deposit -> registration -> search -> claim -> decision -> restored database/photos tested with synthetic fixtures.
- [ ] Anika commits the Wokwi sketch, wiring and genuine serial evidence; perform the handbook's ten-press/hold/reset checks.
- [ ] Aashi commits the UI and verifies registration, search, detail, claim and authenticated staff decisions against this backend.
- [ ] All members run the complete flow using genuine saved Wokwi JSON and the reviewed UI; capture expected/actual results, commit SHA and screenshots without private data.
- [ ] Run and record the recovery exercise on a deliberately created demo dataset; verify photos, claim state and audit after restart.

Record failures as well as successes. Keep the simulation-first gate: backend tests alone do not authorize a claim that hardware acceptance has passed. After this gate, B08 can freeze the API and assemble demo/report evidence.
