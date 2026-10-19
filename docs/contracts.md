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

## Required follow-up routes (not implemented)
| Route | Required contract |
|---|---|
| POST /api/claims | Public {item_id,contact,evidence}; 201 {claim_id,status:"pending"}; 409 unavailable |
| GET /api/admin/claims | Staff; optional status enum pending/approved/rejected; private evidence/contact only here |
| POST /api/admin/claims/{id}/approve | Staff {reason}; 200 {claim_id,status:"approved",item_status:"claimed"}; atomic update + audit; 409 repeated/competing approval |
| POST /api/admin/claims/{id}/reject | Staff {reason}; 200 rejected; item remains available |

Contact cap 120, evidence/reason/notes cap 500; trim fields. Canonical registration values match vocabulary. JPEG/PNG only, 5 MiB maximum, decoded pixel limit (12 MP chosen), UUID path outside public static directory, re-encode to RGB JPEG and remove metadata. Cleanup newly written image after failed insert. No private mark/contact/evidence in public responses.

Future staff routes use the same HTTP Basic dependency; missing configuration rejects startup. Device key is separate. Remote deployment needs HTTPS; current default is loopback only. Future frontend mount /ui; no CORS needed for same-origin. If split development needs CORS, allow explicit localhost:5500 and 127.0.0.1:5500 only.

Anika handoff: same event ID on retry, X-Device-Key, 201/200 success, 401/409 stop and inspect. Aashi handoff: server owns scoring; display parsed facts, clarification, coverage and related labels. Inspect /openapi.json for implemented routes. Registration is implemented; claim contracts remain reserved.

## B04 envelope and error decisions
Public item detail/list fields are id, category, color, brand (nullable), location, status, created_at, mark (nullable), photo_url. Public responses exclude event_id, stored photo_path and all private attributes. Available items only: claimed detail and photo return 404. Listing is ordered by ascending ID, default limit=20, and next_offset is non-null only when another row exists. These choices fill gaps allowed by the handbook.

Registration trims fields and accepts canonical vocabulary strings only (for example bottle/blue, not flask/navy aliases). Empty optional fields become absent/NULL. private_mark is free text capped at 500 characters. Wrong/missing event: 404; duplicate event: 409; corrupt/unsupported image: 422; >5 MiB or >12 MP: 413. Decoded file format controls acceptance, not the supplied MIME header or filename. Photos use UUID JPEG names and no-store responses. Generic storage/database failures return 500; details stay in server logs. Failed database writes roll back attributes and item together and remove the newly written image.

UPLOAD_DIR overrides the default backend/uploads directory. Stop the server before running the read-only orphan audit: python -m app.services.images. It reports unreferenced files and missing referenced files; inspect and back up before manual repair. A crash between filesystem write and database commit can leave an orphan; no automatic deletion races with live registrations.

## B05 search card additions
Existing query/broaden input, parsed facts, results, clarification and score fields are unchanged. Each result now adds category, color, brand (nullable), location, mark (nullable), photo_url, coverage_text (for example "3 of 5 attributes supplied") and match_label. Related matches explicitly say "Related suggestion, different category"; other matches say "Candidate match". Public fields are allowlisted in both SQL and the typed response model. No private mark, contact, evidence, event ID or filesystem path enters a card.

The response envelope adds message: null with results; a clarification message for ambiguous/unknown queries; a no-match message for an eligible search with no results. Aashi should display parsed chips, message, coverage_text and match_label, render untrusted strings via textContent, and resolve photo_url against the API origin. The browser does not recompute scores. Photos may later return 404 if an item becomes unavailable.

The full search response is described in docs/openapi.json and /openapi.json. A score of 100 for a single supplied field means complete agreement on that one field, never ownership probability. Unknown words remain ignored according to the handbook parser; the evaluation reports false positives this can cause.
