from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import connect
from evaluation import isolated_client, load_dataset

AUTH = ("synthetic", "synthetic-evaluation-only")
BODY = {"item_id":101, "contact":"demo@example.invalid", "evidence":"PRIVATE CLAIM EVIDENCE"}
REASON = {"reason":"Compared hidden initials in person"}

@pytest.fixture
def client():
    items, _ = load_dataset()
    with isolated_client(items) as client:
        yield client


def claim(client, **changes):
    response = client.post("/api/claims", json={**BODY, **changes})
    assert response.status_code == 201
    return response.json()["claim_id"]


def decide(client, claim_id, action="approve", auth=AUTH, body=None):
    return client.post(f"/api/admin/claims/{claim_id}/{action}", auth=auth, json=REASON if body is None else body)


def state():
    with connect() as db:
        return {table:[dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY id")]
                for table in ("items","claim_requests","claim_audit")}


def test_two_claims_approval_visibility_and_private_staff_view(client):
    first, second = claim(client), claim(client, contact="other@example.invalid")
    staff = client.get("/api/admin/claims?status=pending", auth=AUTH)
    assert staff.headers["cache-control"] == "no-store"
    rows = staff.json()["claims"]
    assert len(rows) == 2 and rows[0]["private_mark"] == "SYNTHETIC_PRIVATE_SENTINEL"
    assert rows[0]["evidence"] == BODY["evidence"] and rows[0]["audit"] == []
    photo_url = client.get("/api/items/101").json()["photo_url"]
    for response in (client.get("/api/items"), client.get("/api/items/101"),
                     client.post("/api/search",json={"query":"bottle"})):
        for private in [BODY["contact"], BODY["evidence"], "SYNTHETIC_PRIVATE_SENTINEL", "private_mark", "audit"]:
            assert private not in response.text
    approval = decide(client, first)
    assert approval.status_code == 200
    assert approval.json() == {"claim_id":first,"status":"approved","item_status":"claimed"}
    assert decide(client, second).status_code == 409
    assert decide(client, first).status_code == 409
    assert decide(client, first, "reject").status_code == 409
    assert client.post("/api/claims",json=BODY).status_code == 409
    assert client.get("/api/items/101").status_code == 404
    assert client.get(photo_url).status_code == 404
    assert 101 not in [x["id"] for x in client.get("/api/items").json()["items"]]
    assert 101 not in [x["id"] for x in client.post("/api/search",json={"query":"blue milton bottle star"}).json()["results"]]
    pending = client.get("/api/admin/claims?status=pending",auth=AUTH).json()["claims"]
    assert pending[0]["claim_id"] == second and pending[0]["item_status"] == "claimed"
    approved = client.get("/api/admin/claims?status=approved",auth=AUTH).json()["claims"]
    audit = approved[0]["audit"]
    assert len(audit) == 1 and audit[0]["actor"] == AUTH[0]
    assert audit[0]["reason"] == REASON["reason"] and audit[0]["action"] == "approved"
    assert audit[0]["created_at"].endswith("Z")
    # A stale competing claim may be explicitly rejected without changing the item.
    assert decide(client, second, "reject").status_code == 200
    assert state()["items"][0]["status"] == "claimed"
    with TestClient(app) as restarted:
        assert restarted.get("/api/admin/claims?status=approved",auth=AUTH).json()["claims"] == approved


def test_rejection_leaves_item_available_and_other_claim_can_win(client):
    first, second = claim(client), claim(client)
    assert decide(client, first, "reject").json() == {"claim_id":first,"status":"rejected"}
    assert client.get("/api/items/101").status_code == 200
    assert decide(client, first).status_code == 409
    assert decide(client, first, "reject").status_code == 409
    assert decide(client, second).status_code == 200


@pytest.mark.parametrize("auth", [None, ("wrong","wrong")])
def test_staff_routes_401_and_no_mutation(client, auth):
    claim_id = claim(client)
    before = state()
    response = client.get("/api/admin/claims",auth=auth)
    assert response.status_code == 401 and response.headers["www-authenticate"] == "Basic"
    assert decide(client,claim_id,auth=auth).status_code == 401
    assert decide(client,claim_id,"reject",auth=auth).status_code == 401
    assert state() == before


@pytest.mark.parametrize("changes", [
    {"item_id":0}, {"item_id":True}, {"item_id":"101"}, {"contact":" "},
    {"contact":"x"*121}, {"evidence":" "}, {"evidence":"x"*501},
    {"status":"approved"}, {"actor":"staff"}, {"contact":None},
])
def test_claim_validation_and_no_client_authority(client, changes):
    assert client.post("/api/claims",json={**BODY,**changes}).status_code == 422
    assert state()["claim_requests"] == []


@pytest.mark.parametrize("body", [{"reason":" "},{"reason":"x"*501},{},
                                   {"reason":"ok","actor":"forged"},{"reason":"ok","status":"approved"}])
def test_decision_validation_no_mutation(client, body):
    claim_id = claim(client)
    before = state()
    assert decide(client, claim_id, body=body).status_code == 422
    assert decide(client, claim_id, "reject", body=body).status_code == 422
    assert state() == before


def test_trim_boundaries_unknown_ids_and_status_filter(client):
    claim_id = claim(client, contact=" " + "x"*120 + " ", evidence=" " + "x"*500 + " ")
    row = state()["claim_requests"][0]
    assert len(row["contact"]) == 120 and len(row["evidence"]) == 500
    assert decide(client,claim_id,body={"reason":" " + "r"*500 + " "}).status_code == 200
    assert len(state()["claim_audit"][0]["reason"]) == 500
    assert client.post("/api/claims",json={**BODY,"item_id":9999}).status_code == 404
    assert decide(client,9999).status_code == 404
    assert decide(client,9999,"reject").status_code == 404
    assert decide(client,0).status_code == 422
    assert client.get("/api/admin/claims?status=anything",auth=AUTH).status_code == 422
    assert client.get("/api/admin/claims?status=rejected",auth=AUTH).json() == {"claims":[]}
    assert client.post("/api/claims",json={**BODY,"item_id":105}).status_code == 409


@pytest.mark.parametrize("action", ["approve","reject"])
def test_audit_failure_rolls_back_whole_decision(client, action):
    claim_id = claim(client)
    with connect() as db:
        db.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON claim_audit BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
    before = state()
    response = decide(client,claim_id,action)
    assert response.status_code == 500 and response.json() == {"detail":"Database operation failed"}
    assert state() == before


def test_concurrent_approvals_have_one_winner(client):
    ids = [claim(client),claim(client)]
    barrier = Barrier(2)
    def attempt(claim_id):
        barrier.wait(timeout=10)
        return decide(client,claim_id).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(attempt,ids))
    assert sorted(statuses) == [200,409]
    snapshot = state()
    assert len(snapshot["claim_audit"]) == 1
    assert sum(c["status"] == "approved" for c in snapshot["claim_requests"]) == 1
    assert sum(c["status"] == "pending" for c in snapshot["claim_requests"]) == 1


def test_concurrent_approve_reject_same_claim_has_one_decision(client):
    claim_id = claim(client)
    barrier = Barrier(2)
    def attempt(action):
        barrier.wait(timeout=10)
        return decide(client,claim_id,action).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(attempt,["approve","reject"]))
    assert sorted(statuses) == [200,409]
    snapshot = state()
    assert len(snapshot["claim_audit"]) == 1
    decision = snapshot["claim_requests"][0]["status"]
    assert snapshot["claim_audit"][0]["action"] == decision
    assert snapshot["items"][0]["status"] == ("claimed" if decision == "approved" else "available")
