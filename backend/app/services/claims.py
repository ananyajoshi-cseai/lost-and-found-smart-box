"""Short SQLite transactions make claim decisions indivisible."""
from ..database import connect


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def submit_claim(item_id, contact, evidence):
    with connect() as db:
        # Serialize with approval before checking availability.
        db.execute("BEGIN IMMEDIATE")
        item = db.execute("SELECT status FROM items WHERE id=?", (item_id,)).fetchone()
        if item is None:
            raise NotFound("Item not found")
        if item["status"] != "available":
            raise Conflict("Item is unavailable")
        cursor = db.execute("INSERT INTO claim_requests(item_id,contact,evidence) VALUES(?,?,?)",
                            (item_id, contact, evidence))
        claim_id = cursor.lastrowid
    return {"claim_id": claim_id, "status": "pending"}


def decide_claim(claim_id, actor, reason, action):
    if action not in {"approved", "rejected"}:
        raise ValueError("Unsupported decision")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        claim = db.execute("SELECT item_id,status FROM claim_requests WHERE id=?", (claim_id,)).fetchone()
        if claim is None:
            raise NotFound("Claim not found")
        if claim["status"] != "pending":
            raise Conflict("Claim already decided")
        if action == "approved":
            changed = db.execute("UPDATE items SET status='claimed' WHERE id=? AND status='available'",
                                 (claim["item_id"],)).rowcount
            if changed != 1:
                raise Conflict("Item is unavailable; another claim may already be approved")
        db.execute("UPDATE claim_requests SET status=? WHERE id=?", (action, claim_id))
        db.execute("INSERT INTO claim_audit(claim_id,actor,action,reason) VALUES(?,?,?,?)",
                   (claim_id, actor, action, reason))
        # connect() commits on success and rolls back ALL writes on any exception.
    result = {"claim_id": claim_id, "status": action}
    if action == "approved":
        result["item_status"] = "claimed"
    return result


def list_claims(status=None):
    with connect() as db:
        # A read transaction keeps the claim and audit views in the same snapshot.
        db.execute("BEGIN")
        sql = """SELECT c.id AS claim_id,c.item_id,c.contact,c.evidence,c.status,c.created_at,
                 i.status AS item_status,a.value AS private_mark
                 FROM claim_requests c JOIN items i ON i.id=c.item_id
                 LEFT JOIN item_attributes a ON a.item_id=i.id AND a.name='private_mark' AND a.private=1"""
        params = ()
        if status is not None:
            sql += " WHERE c.status=?"
            params = (status,)
        rows = db.execute(sql + " ORDER BY c.id", params).fetchall()
        result = []
        for row in rows:
            audit = db.execute("SELECT actor,action,reason,created_at FROM claim_audit WHERE claim_id=? ORDER BY id",
                               (row["claim_id"],)).fetchall()
            result.append({**dict(row), "audit": [dict(entry) for entry in audit]})
    return {"claims": result}
