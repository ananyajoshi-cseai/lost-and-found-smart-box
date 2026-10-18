from fastapi import APIRouter
from ..ai.engine import parse, rank
from ..database import connect
from ..schemas import SearchIn

router = APIRouter()


@router.post("/api/search")
def search(body: SearchIn):
    parsed = parse(body.query)
    message = None
    if parsed["ambiguous"]:
        message = "Please clarify: " + ", ".join(parsed["ambiguous"])
    elif not parsed["positive"]:
        message = "Please provide a known category, color, brand, location or public mark."
    if message:
        return {"parsed": parsed, "results": [], "clarification": message}
    with connect() as db:
        rows = db.execute("SELECT i.id,i.category,i.color,i.brand,i.location,i.status,a.value AS mark FROM items i LEFT JOIN item_attributes a ON a.item_id=i.id AND a.name='mark' AND a.private=0 WHERE i.status=?", ("available",)).fetchall()
    return {"parsed": parsed, "results": rank(parsed, [dict(row) for row in rows], body.broaden), "clarification": None}
