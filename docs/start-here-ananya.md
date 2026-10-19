# Start here, Ananya

## 1. Understand the repository
Open the root README. `main` is the shared checkpoint; do your work on `backend/ananya`. The other members own their respective folders. A commit is a named snapshot; a pull request asks a teammate to review snapshots before merging.

```powershell
git switch backend/ananya
git status
```

## 2. Run your first checkpoint
Follow `backend/README.md` to set credentials and launch the server. Inspect `app/main.py`: `@app.get('/health')` connects the URL to a function, whose dictionary becomes JSON. Test it in `/docs` with **Try it out Ã¢â€ â€™ Execute**. Expected status: 200.

## 3. Inspect SQLite
Read `app/schema.sql`, then run `python -m app.database` using your virtual-environment interpreter. Events, items and claims are separate records. A UNIQUE event reference prevents duplicate registration. Every connection turns foreign keys on. `database.connect()` commits success, rolls back errors and closes the connection.

## 4. Try duplicate-safe deposits
With the server running, open another terminal at the repository root, set DEVICE_KEY to the same value and run:

```powershell
$env:DEVICE_KEY = Read-Host 'Enter the same device key'
.\backend\.venv\Scripts\python.exe hardware/simulation/replay.py hardware/simulation/event.example.json
.\backend\.venv\Scripts\python.exe hardware/simulation/replay.py hardware/simulation/event.example.json
```

Expect 201/duplicate:false then 200/duplicate:true. This file is synthetic, not evidence of a Wokwi press. Anika later substitutes her genuine saved serial JSON.

## 5. Follow one query through the AI
Read `vocabulary.py`, `parser.py`, `ontology.py`, then `scoring.py`. Run `tests/test_ai.py`. Explain why 'navy flask' becomes blue+bottle, why 'not blue' excludes blue, and why 'red blue bottle' asks for clarification. BFS traverses category nodes, not database rows. Derive the 90-point worked example in `docs/ai-decisions.md`.

## 6. Review the integration boundary
`docs/contracts.md` preserves the handbook's paths, field names and status codes. The generated `/openapi.json` describes only implemented routes. Aashi must not call a planned route until its issue is finished. The server computes scores; the browser only displays them.

## 7. B04 is implemented: run the registration exercise
Read the implemented registration and image handling in `app/routers/items.py` and `app/services/images.py`. Follow handbook pages 19-22: canonical validation, 5 MiB limit, Pillow decoding and JPEG re-encoding, UUID filename, one transaction for item/attributes, orphan cleanup on failure, and safe public detail/photo routes. Run docs/b04-walkthrough.md and the upload tests. Then complete B05 evaluation, B06 claims and B07 integration. B05 evaluation and B06 claim routes are now implemented; see their walkthroughs. B07 backend integration and recovery are implemented; follow docs/b07-walkthrough.md. Actual frontend/Wokwi team acceptance remains open.

## 8. Commit each finished checkpoint
From the repo root, inspect `git diff`, run tests, add only your changed files, commit with a concrete message and push your branch. Open a PR into main. Have Aashi review browser-facing responses and Anika review event behavior. Never force-push main.
