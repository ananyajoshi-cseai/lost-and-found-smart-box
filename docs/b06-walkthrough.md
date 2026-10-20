# B06: submit a claim and record a staff decision

Use synthetic practice data only. This is a backend exercise in /docs; the staff UI is separate. The staff decision follows an in-person check; no score, photo recognition or QR scan approves ownership.

## 1. Prepare an available item
Start the backend using backend/README.md. Follow the B04 exercise to register a new practice item. Record its integer item ID and confirm it appears in GET /api/items. Use a new event ID if the old practice event was already registered.

## 2. Submit two competing claims
In /docs, expand POST /api/claims and choose Try it out. Replace 101 with your actual available item ID:

```json
{"item_id":101,"contact":"first@example.invalid","evidence":"Practice hidden initials"}
```

Execute: expect 201 and {claim_id:...,status:"pending"}. Note the claim ID. Submit a second request for the same item with contact second@example.invalid and different synthetic evidence. Both may be pending. This is intentional: a submission is a request, not an award of ownership. Do not automatically retry a submission after uncertain network delivery; this route has no idempotency key.

## 3. Inspect the staff-only list
Click Authorize in /docs and supply the STAFF_USERNAME/STAFF_PASSWORD set in your server terminal. Call GET /api/admin/claims with status=pending. Staff can see contact, evidence, private_mark and item_status. Those fields are restricted to the staff dashboard; credentials must not be stored in JavaScript or localStorage.

Without credentials, the list and decision routes return 401. Public search/detail must never show private evidence or contact information.

## 4. Approve one claim after your simulated check
Expand POST /api/admin/claims/{claim_id}/approve, enter the first claim ID and submit:

```json
{"reason":"Compared hidden initials in the supervised practice exercise"}
```

Expect 200 with status=approved and item_status=claimed. The database stores your authenticated staff username as actor; the request cannot choose an actor. Repeat the approval: expect 409, with no second audit entry.

## 5. Verify the return and competing claim
Search for the item: that ID must no longer appear. Its public detail/photo routes now return 404. Try approving the second claim: expect 409 because the item is already claimed. Its claim can remain pending; the staff response shows item_status=claimed. You may explicitly reject it with a reason to record the disposition. It must not be silently approved or rejected by the browser.

GET /api/admin/claims?status=approved shows the approved entry with audit containing actor, action, reason and UTC timestamp. Stop and restart the server; the result persists.

## 6. Try rejection on a separate available item
Register another practice item and submit a claim. Use /reject with a reason such as "Practice evidence did not match". The claim becomes rejected, but the available item remains searchable. A different pending claim for that item may still be approved. A rejected claim cannot be reopened through these routes.

## 7. Understand the transaction
Read app/services/claims.py. BEGIN IMMEDIATE reserves the SQLite write transaction before reading state. Approval updates only an item whose status is still available, then saves claim status and audit. The connection helper commits all changes together; an exception rolls everything back. The database's unique approved-claim index adds another safeguard.

Read tests/test_claims.py: two simultaneous approvals have one winner; approval versus rejection of the same claim has one final decision; an injected audit failure leaves both item and claim unchanged. The staff identity comes from require_staff, not a form field.

## 8. Run the suite
From backend in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests use synthetic fixtures and temporary images/databases, not your practice records. The next checkpoint is B07: connect the team's actual frontend/device flow, same-origin /ui serving, and backup/restore recovery.
