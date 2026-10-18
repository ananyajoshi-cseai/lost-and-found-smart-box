# API contract v1

Source: handbook pages 20-22; exact extracted text in handbook-api-reference.txt. All timestamps UTC ISO, item IDs integers, snake_case keys. 422 validation; 404 unknown ID; 409 conflict; 401 invalid/missing credentials. Framework error shape: {"detail":...}; validation detail is a list. No stack traces in responses.

## Implemented now
| Route | Input/access | Output |
|---|---|---|
| GET /health | Public | 200 {"status":"ok"} |
| POST /api/device/events | X-Device-Key; event_id 1-80 ASCII letters/digits/_/-, device_id 1-40, kind="deposit"; extra keys forbidden | 201 new, 200 identical retry, 409 conflicting body |
| GET /api/admin/events | HTTP Basic staff; pending=true default | 200 {"events":[...]} without registered events; pending=false lists all |
| POST /api/search | Public; query 1-300 chars, broaden=false default | 200 {"parsed":...,"results":[],"clarification":null or message} |

Event example: {"event_id":"box01-synthetic-1","device_id":"box01","kind":"deposit"}. Response includes these fields plus server created_at and duplicate boolean. That flat envelope is a project choice; the handbook specifies statuses and duplicate but not a full envelope.

Parsed example: {"positive":{"category":"bottle","color":"blue"},"excluded":{},"ambiguous":[]}. Result contains id, score, coverage (out of 5), denominator, reasons [{field,weight,points,matched}], strong_candidate and related. These exact envelope/inner keys fill specification gaps; they do not replace handbook requirements. Search currently returns ranked IDs and explanations; safe display attributes/photo links are a B04/B05 integration follow-up.

## Required follow-up routes (not implemented)
| Route | Required contract |
|---|---|
| POST /api/items | Staff multipart event_id/category/color/location/photo; optional brand/mark/private_mark; 201 {id,status:"available",event_id} |
| GET /api/items | Public available only; limit 1-50, offset>=0; {items:[...],next_offset:null or next offset} |
| GET /api/items/{id} | Public safe detail; 404 absent, claimed may say unavailable |
| GET /api/items/{id}/photo | Public sanitized JPEG only if available; otherwise 404 |
| POST /api/claims | Public {item_id,contact,evidence}; 201 {claim_id,status:"pending"}; 409 unavailable |
| GET /api/admin/claims | Staff; optional status enum pending/approved/rejected; private evidence/contact only here |
| POST /api/admin/claims/{id}/approve | Staff {reason}; 200 {claim_id,status:"approved",item_status:"claimed"}; atomic update + audit; 409 repeated/competing approval |
| POST /api/admin/claims/{id}/reject | Staff {reason}; 200 rejected; item remains available |

Contact cap 120, evidence/reason/notes cap 500; trim fields. Canonical registration values match vocabulary. JPEG/PNG only, 5 MiB maximum, decoded pixel limit (12 MP chosen), UUID path outside public static directory, re-encode to RGB JPEG and remove metadata. Cleanup newly written image after failed insert. No private mark/contact/evidence in public responses.

Future staff routes use the same HTTP Basic dependency; missing configuration rejects startup. Device key is separate. Remote deployment needs HTTPS; current default is loopback only. Future frontend mount /ui; no CORS needed for same-origin. If split development needs CORS, allow explicit localhost:5500 and 127.0.0.1:5500 only.

Anika handoff: same event ID on retry, X-Device-Key, 201/200 success, 401/409 stop and inspect. Aashi handoff: server owns scoring; display parsed facts, clarification, coverage and related labels. Inspect /openapi.json for implemented routes. Registration/claim contracts are reserved but unavailable until their issues pass.
