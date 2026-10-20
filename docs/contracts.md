# API contract v1

Source: handbook pages 20-22; exact extracted text in handbook-api-reference.txt. All timestamps UTC ISO, item IDs integers, snake_case keys. 422 validation; 404 unknown ID; 409 conflict; 401 invalid/missing credentials. Framework error shape: {"detail":...}; validation detail is a list. No stack traces in responses.

## Implemented now
| Route | Input/access | Output |
|---|---|---|
| GET /health | Public | 200 {"status":"ok"} |
| POST /api/device/events | X-Device-Key; event_id 1-80 ASCII letters/digits/_/-, device_id 1-40, kind="deposit"; extra keys forbidden | 201 new, 200 identical retry, 409 conflicting body |
| GET /api/admin/events | HTTP Basic staff; pending=true default | 200 {"events":[...]} without registered events; pending=false lists all |
| POST /api/search | Public; query 1-300 chars, broaden=false default | 200 {"parsed":...,"results":[],"clarification":null or message} |

### Implemented B04 routes
| Route | Contract |
|---|---|
| POST /api/items | Staff multipart event_id/category/color/location/photo; optional brand/mark/private_mark; 201 {id,status:"available",event_id} |
| GET /api/items | Public available only; limit 1-50, offset>=0; {items:[...],next_offset:null or next offset} |
| GET /api/items/{id} | Public safe detail; 404 absent, claimed may say unavailable |
| GET /api/items/{id}/photo | Public sanitized JPEG only if available; otherwise 404 |


Event example: {"event_id":"box01-synthetic-1","device_id":"box01","kind":"deposit"}. Response includes these fields plus server created_at and duplicate boolean. That flat envelope is a project choice; the handbook specifies statuses and duplicate but not a full envelope.

Parsed example: {"positive":{"category":"bottle","color":"blue"},"excluded":{},"ambiguous":[]}. Result contains id, score, coverage (out of 5), denominator, reasons [{field,weight,points,matched}], strong_candidate and related. These exact envelope/inner keys fill specification gaps; they do not replace handbook requirements. Search currently returns ranked IDs and explanations; safe attributes and photo_url are also included directly in each search result (B05).

## Implemented B06 claim and administration routes
| Route | Required contract |
|---|---|
| POST /api/claims | Public {item_id,contact,evidence}; 201 {claim_id,status:"pending"}; 409 unavailable |
| GET /api/admin/claims | Staff; optional status enum pending/approved/rejected; private evidence/contact only here |
| POST /api/admin/claims/{id}/approve | Staff {reason}; 200 {claim_id,status:"approved",item_status:"claimed"}; atomic update + audit; 409 repeated/competing approval |
| POST /api/admin/claims/{id}/reject | Staff {reason}; 200 rejected; item remains available |

Contact cap 120, evidence/reason/notes cap 500; trim fields. Canonical registration values match vocabulary. JPEG/PNG only, 5 MiB maximum, decoded pixel limit (12 MP chosen), UUID path outside public static directory, re-encode to RGB JPEG and remove metadata. Cleanup newly written image after failed insert. No private mark/contact/evidence in public responses.

All staff routes use the same HTTP Basic dependency; missing configuration rejects startup. Device key is separate. Remote deployment needs HTTPS; current default is loopback only. Frontend mount /ui is implemented (503 until index.html exists); no CORS needed for same-origin. If split development needs CORS, allow explicit localhost:5500 and 127.0.0.1:5500 only.

Device integration: same event ID on retry, X-Device-Key, 201/200 success, 401/409 stop and inspect. Frontend integration: server owns scoring; display parsed facts, clarification, coverage and related labels. Inspect /openapi.json for implemented routes. Registration and claim routes are implemented.

## B04 envelope and error decisions
Public item detail/list fields are id, category, color, brand (nullable), location, status, created_at, mark (nullable), photo_url. Public responses exclude event_id, stored photo_path and all private attributes. Available items only: claimed detail and photo return 404. Listing is ordered by ascending ID, default limit=20, and next_offset is non-null only when another row exists. These choices fill gaps allowed by the handbook.

Registration trims fields and accepts canonical vocabulary strings only (for example bottle/blue, not flask/navy aliases). Empty optional fields become absent/NULL. private_mark is free text capped at 500 characters. Wrong/missing event: 404; duplicate event: 409; corrupt/unsupported image: 422; >5 MiB or >12 MP: 413. Decoded file format controls acceptance, not the supplied MIME header or filename. Photos use UUID JPEG names and no-store responses. Generic storage/database failures return 500; details stay in server logs. Failed database writes roll back attributes and item together and remove the newly written image.

UPLOAD_DIR overrides the default backend/uploads directory. Stop the server before running the read-only orphan audit: python -m app.services.images. It reports unreferenced files and missing referenced files; inspect and back up before manual repair. A crash between filesystem write and database commit can leave an orphan; no automatic deletion races with live registrations.

## B05 search card additions
Existing query/broaden input, parsed facts, results, clarification and score fields are unchanged. Each result now adds category, color, brand (nullable), location, mark (nullable), photo_url, coverage_text (for example "3 of 5 attributes supplied") and match_label. Related matches explicitly say "Related suggestion, different category"; other matches say "Candidate match". Public fields are allowlisted in both SQL and the typed response model. No private mark, contact, evidence, event ID or filesystem path enters a card.

The response envelope adds message: null with results; a clarification message for ambiguous/unknown queries; a no-match message for an eligible search with no results. The interface displays parsed chips, message, coverage_text and match_label, renders untrusted strings via textContent, and resolves photo_url against the API origin. The browser does not recompute scores. Photos may later return 404 if an item becomes unavailable.

The full search response is described in docs/openapi.json and /openapi.json. A score of 100 for a single supplied field means complete agreement on that one field, never ownership probability. Unknown words remain ignored according to the handbook parser; the evaluation reports false positives this can cause.

## B06 decisions and staff-only envelope
POST /api/claims accepts only item_id/contact/evidence. item_id is a positive JSON integer; contact/evidence are trimmed, nonempty strings capped at 120/500 characters. Extra fields (including status or actor) are rejected with 422. Unknown item: 404; unavailable item: 409. Receipt is exactly {claim_id,status:"pending"}. Multiple pending claims for an available item are allowed; submissions are not ownership proof or idempotent requests.

GET /api/admin/claims returns {claims:[...]}, ordered by claim_id ascending; omitted status returns all, otherwise pending/approved/rejected only. Staff entries contain claim_id, item_id, contact, evidence, status, created_at, item_status, private_mark (nullable), and audit. Each audit entry contains actor/action/reason/created_at. private_mark is included only here to let staff compare hidden details. This documented envelope fills the handbook's unspecified admin response shape. Staff response and decision/receipt responses use Cache-Control: no-store. This list is intended for the small supervised demo, not a paginated production inbox.

Approve returns exactly {claim_id,status:"approved",item_status:"claimed"}. Reject returns {claim_id,status:"rejected"}. Both require HTTP Basic and a trimmed, nonempty reason <=500 characters. Client-supplied actor/status are forbidden; actor comes from authenticated staff. Missing credentials: 401 with Basic challenge; unknown positive claim ID: 404; decided claim or competing approval: 409. Invalid nonpositive claim ID: 422. No reset/reopen endpoint is provided.

Submission and decisions use BEGIN IMMEDIATE transactions. Approval conditionally changes an available item to claimed, updates the claim and appends audit together; rejection changes only claim/audit. Any failure rolls all writes back. A rejected claim cannot later be approved. Other pending claims stay pending after one approval; their item_status=claimed tells the UI they cannot win. Staff can explicitly reject these remaining claims, preserving the already-claimed item status. Private contact/evidence/mark/audit do not appear in public list/detail/search/photo routes.

The no-ML scoring engine never approves claims. Staff must independently verify ownership; a QR reference or high score grants no approval permission. Rate limiting, institutional identity and retention automation remain deployment work before any service is exposed outside the supervised local demo; these have not been silently claimed implemented.

## B07 hosting and recovery

Existing API envelopes are unchanged. /ui redirects to /ui/; only frontend/ is mounted. Optional CORS_ORIGINS accepts comma-separated http://localhost:5500 and http://127.0.0.1:5500 only, with GET/POST, Authorization/Content-Type and credential support. The default is no CORS middleware. Recovery is an offline CLI, not a public HTTP endpoint. See b07-walkthrough.md for tested behavior, safe restore commands and outstanding team acceptance.
