import sqlite3
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import connect

@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db"))
 monkeypatch.setenv("DEVICE_KEY","test-device")
 monkeypatch.setenv("STAFF_USERNAME","test-staff")
 monkeypatch.setenv("STAFF_PASSWORD","test-password")
 with TestClient(app) as client:
  yield client

EVENT={"event_id":"box01-demo-1","device_id":"box01","kind":"deposit"}
KEY={"X-Device-Key":"test-device"}
AUTH=("test-staff","test-password")

def test_health(client):
 r=client.get("/health")
 assert r.status_code == 200 and r.json() == {"status":"ok"}

def test_events_idempotency_conflict_and_restart(client):
 assert client.post("/api/device/events",json=EVENT).status_code == 401
 a=client.post("/api/device/events",json=EVENT,headers=KEY)
 b=client.post("/api/device/events",json=EVENT,headers=KEY)
 assert a.status_code == 201 and a.json()["duplicate"] is False
 assert b.status_code == 200 and b.json()["duplicate"] is True
 assert a.json()["created_at"] == b.json()["created_at"]
 assert client.post("/api/device/events",json={**EVENT,"device_id":"other"},headers=KEY).status_code == 409
 assert client.get("/api/admin/events").status_code == 401
 assert len(client.get("/api/admin/events",auth=AUTH).json()["events"]) == 1
 with TestClient(app) as restarted:
  assert len(restarted.get("/api/admin/events",auth=AUTH).json()["events"]) == 1

@pytest.mark.parametrize("change", [{"event_id":"bad id"},{"kind":"pickup"},{"extra":True},{"event_id":""},{"device_id":"x"*41}])
def test_event_validation(client,change):
 assert client.post("/api/device/events",json={**EVENT,**change},headers=KEY).status_code == 422

def test_schema_and_live_search(client):
 client.post("/api/device/events",json=EVENT,headers=KEY)
 with connect() as db:
  assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
  db.execute("INSERT INTO items(id,event_id,category,color,brand,location,photo_path) VALUES(101,?,'bottle','blue','milton','library','synthetic.jpg')",(EVENT["event_id"],))
  db.execute("INSERT INTO item_attributes VALUES(101,'private_mark','SECRET',1)")
 assert client.get("/api/admin/events",auth=AUTH).json() == {"events":[]}
 r=client.post("/api/search",json={"query":"navy Milton flask"})
 assert r.status_code == 200 and r.json()["results"][0]["score"] == 100
 assert "SECRET" not in r.text and "photo_path" not in r.text
 assert client.post("/api/search",json={"query":"red blue bottle"}).json()["clarification"]
 assert client.post("/api/search",json={"query":"something"}).json()["results"] == []
 with pytest.raises(sqlite3.IntegrityError):
  with connect() as db:
   db.execute("INSERT INTO items(event_id,category,color,location,photo_path) VALUES('missing','bottle','blue','library','x')")
 with pytest.raises(sqlite3.IntegrityError):
  with connect() as db:
   db.execute("INSERT INTO items(event_id,category,color,location,photo_path) VALUES(?,'bottle','blue','library','x')",(EVENT["event_id"],))
 with connect() as db:
  db.execute("UPDATE items SET status='claimed' WHERE id=101")
 assert client.post("/api/search",json={"query":"bottle"}).json()["results"] == []

def test_missing_configuration(monkeypatch):
 monkeypatch.delenv("DEVICE_KEY",raising=False)
 with pytest.raises(RuntimeError,match="DEVICE_KEY"):
  with TestClient(app): pass


def test_claim_constraints_and_append_only_audit(client):
 client.post("/api/device/events",json=EVENT,headers=KEY)
 with connect() as db:
  db.execute("INSERT INTO items(id,event_id,category,color,location,photo_path) VALUES(101,?,'bottle','blue','library','synthetic.jpg')",(EVENT["event_id"],))
  db.execute("INSERT INTO claim_requests(id,item_id,contact,evidence,status) VALUES(1,101,'demo@example.invalid','test','approved')")
  db.execute("INSERT INTO claim_audit(claim_id,actor,action,reason) VALUES(1,'test-staff','approved','synthetic check')")
 with pytest.raises(sqlite3.IntegrityError):
  with connect() as db:
   db.execute("INSERT INTO claim_requests(item_id,contact,evidence,status) VALUES(101,'other@example.invalid','test','approved')")
 for statement in ["UPDATE claim_audit SET reason='changed'", "DELETE FROM claim_audit"]:
  with pytest.raises(sqlite3.IntegrityError):
   with connect() as db: db.execute(statement)
 with connect() as db:
  assert db.execute("SELECT COUNT(*) FROM claim_audit").fetchone()[0] == 1
