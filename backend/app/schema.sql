PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS device_events (
 event_id TEXT PRIMARY KEY, device_id TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind='deposit'),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE IF NOT EXISTS items (
 id INTEGER PRIMARY KEY, event_id TEXT NOT NULL UNIQUE REFERENCES device_events(event_id),
 category TEXT NOT NULL, color TEXT NOT NULL, brand TEXT, location TEXT NOT NULL,
 photo_path TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available','claimed')),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TABLE IF NOT EXISTS item_attributes (
 item_id INTEGER NOT NULL REFERENCES items(id), name TEXT NOT NULL, value TEXT NOT NULL,
 private INTEGER NOT NULL DEFAULT 0 CHECK(private IN (0,1)), PRIMARY KEY(item_id,name)
);
CREATE TABLE IF NOT EXISTS claim_requests (
 id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL REFERENCES items(id),
 contact TEXT NOT NULL CHECK(length(contact) BETWEEN 1 AND 120),
 evidence TEXT NOT NULL CHECK(length(evidence) BETWEEN 1 AND 500),
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS one_approved_claim ON claim_requests(item_id) WHERE status='approved';
CREATE TABLE IF NOT EXISTS claim_audit (
 id INTEGER PRIMARY KEY, claim_id INTEGER NOT NULL REFERENCES claim_requests(id), actor TEXT NOT NULL,
 action TEXT NOT NULL CHECK(action IN ('approved','rejected')),
 reason TEXT NOT NULL CHECK(length(reason) BETWEEN 1 AND 500),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON claim_audit
 BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON claim_audit
 BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
