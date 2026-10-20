# Frontend integration guide

Backend checkpoint: merged PR #12, commit 0626bb8e63cf0ae677026df05fb12826912b1231. Contract v1 is the integration baseline; final freeze awaits team acceptance.

## Launch and contract

Follow backend/README.md. Default API origin is http://127.0.0.1:8000 on the same laptop. /docs is interactive; /openapi.json is generated from the running implementation. The checked-in docs/openapi.json is the API snapshot; docs/contracts.md explains envelopes and decisions where the handbook did not specify one.

Put the reviewed index.html and assets in frontend/ and open /ui/. Until index.html exists, expect 503. Relative assets and /api/ paths work on the same origin. Optional split-server CORS is documented in b07-walkthrough.md. Do not embed credentials in HTML/JS or persist them in localStorage. Device key and staff credentials are separate. Keep private claim details out of logs/screenshots.

## Requests to build against

- Deposit event: POST /api/device/events with X-Device-Key and {"event_id":"demo-001","device_id":"box01","kind":"deposit"}. New=201; identical retry=200; changed payload with same ID=409. The replay script supplies this; the browser does not need the device secret.
- Pending queue: GET /api/admin/events with staff HTTP Basic.
- Registration: POST /api/items with staff HTTP Basic and multipart fields event_id, category, color, location, photo; optional brand, mark, private_mark. Use FormData and let the browser set the multipart boundary. Send canonical values from the vocabulary, not query aliases. Successful receipt is {id,status:"available",event_id}.
- Search: POST /api/search with {"query":"navy Milton flask","broaden":false}. Display parsed facts, clarification/message, returned reasons, coverage_text and match_label. Render untrusted strings via textContent. Do not recompute scores or turn a strong_candidate flag into approval.
- Detail/photo: use returned photo_url against the API origin. A claimed item or photo can return 404; show an unavailable state rather than retaining a misleading claim button.
- Claim: POST /api/claims with {"item_id":1,"contact":"demo@example.invalid","evidence":"synthetic identifying detail"}. Receipt {claim_id,status:"pending"} is not an approval. Use the actual registered item ID.
- Staff list: GET /api/admin/claims (optional status filter); response {claims:[...]}, including private evidence and audit. Never copy these fields into public cards.
- Decision: POST /api/admin/claims/{id}/approve or /reject with staff HTTP Basic and {"reason":"human verification explanation"}. Handle 409 for a decided claim or competing approval. Refresh item and claim state after success.

Use 401 for credential errors, 404 for missing/unavailable records, 409 for conflicts, 413 for upload limits and 422 for input errors. Preserve visible server failures; never show success before the request succeeds. Framework errors use detail; validation detail can be a list.

## Evidence to return during integration

For each defect record commit, page URL, steps, method/path, sanitized body, HTTP status, expected/actual result and a screenshot without secrets or private records. Complete the genuine-client flow in b07-walkthrough.md and record the IDs in the handbook's team log. Test keyboard access, 360 px layout, no matches, ambiguity, unauthorized staff access, upload failures and two competing claims. Those UI tests are not yet claimed passed.
