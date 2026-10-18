# B04: turn a deposit event into a searchable item

This exercise uses only software and an ordinary sample photo. No hardware or ML is required. Use your own harmless photo without people or private identifying details. The software removes image metadata; it cannot recognize or hide private details visible in the pixels.

## 1. Start your backend
Use backend/README.md from the backend folder. Set DEVICE_KEY, STAFF_USERNAME and STAFF_PASSWORD in the server terminal, then launch Uvicorn. The existing virtual environment is ready; no new dependencies were added. Open http://127.0.0.1:8000/docs.

## 2. Create a deposit event
Expand POST /api/device/events, choose Try it out, and supply X-Device-Key with the value from your server terminal. Use this JSON:

```json
{"event_id":"box01-b04-practice-1","device_id":"box01","kind":"deposit"}
```

Execute: expect 201. If you already used the same ID with the same body, 200 is correct. The event is a pending registration slot; it is not yet an item.

## 3. Register your practice item
In /docs, use Authorize to enter your local staff username/password. Expand POST /api/items and choose Try it out. Fill:

| Field | Value |
|---|---|
| event_id | box01-b04-practice-1 |
| category | bottle |
| color | blue |
| location | library |
| brand | milton |
| mark | star |
| private_mark | practice hidden initials |
| photo | Select a JPEG or PNG under 5 MiB and 12 megapixels |

These are synthetic practice facts; do not use a real claim. Execute: expect 201 with id, status=available and event_id. Save the returned integer ID. A second registration for this event returns 409. Use a new event ID for a different item.

## 4. Inspect the public view
Run GET /api/items and GET /api/items/{item_id}. The private mark and internal filename must be absent. Open the returned photo_url on the same server; it is a re-encoded JPEG. GET /api/admin/events should no longer show the registered event when pending=true.

## 5. Search using an alias
POST /api/search with:

```json
{"query":"navy Milton flask star","broaden":false}
```

Expect this item among the ranked matches, with explicit scoring reasons. Other matching records may rank ahead by score or ID; top three is the maximum. Photos are never parsed by the AI. POST /api/search with 'bottle not blue' must exclude the blue item.

## 6. Read the implementation in this order
1. routers/items.py: staff authentication, validation and the event checks.
2. services/images.py: byte/pixel limits, decoding, metadata removal and generated filenames.
3. routers/items.py: one SQLite transaction for item and attributes; cleanup on failure.
4. Public list/detail/photo functions: explicit field allowlist and available-only behavior.
5. tests/test_items.py: complete flow, malformed uploads, duplicate race and rollback evidence.

A transaction means the item and its attributes either both save or neither saves. File storage is separate, so the failure path explicitly removes the newly written JPEG. If the process crashes mid-write, run the read-only audit while the server is stopped and inspect its report.

## 7. Run the automated checks
From backend in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests create their own images and temporary databases; they do not modify your practice data. The next task is B05 evaluation and search-card integration, then B06 claim decisions. B04 alone does not prove the Wokwi or full return workflow.

Implementation references: [FastAPI multipart forms/files](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/) and [Pillow image verification](https://pillow.readthedocs.io/en/stable/reference/Image.html). Project-specific rules come from handbook pages 19-22.
