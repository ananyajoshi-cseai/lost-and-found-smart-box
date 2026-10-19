from fastapi import APIRouter
from ..ai.engine import parse, rank
from ..database import connect
from ..schemas import SearchIn, SearchOut

router = APIRouter()


@router.post("/api/search", response_model=SearchOut)
def search(body: SearchIn):
    parsed = parse(body.query)
    clarification = None
    if parsed["ambiguous"]:
        clarification = "Please clarify: " + ", ".join(parsed["ambiguous"])
    elif not parsed["positive"]:
        clarification = "Please provide a known category, color, brand, location or public mark."
    if clarification:
        return {"parsed": parsed, "results": [], "clarification": clarification, "message": clarification}
    # Only public fields are read. Private attributes never enter the ranker.
    with connect() as db:
        rows = db.execute("SELECT i.id,i.category,i.color,i.brand,i.location,i.status,a.value AS mark FROM items i LEFT JOIN item_attributes a ON a.item_id=i.id AND a.name='mark' AND a.private=0 WHERE i.status=?", ("available",)).fetchall()
    items = [dict(row) for row in rows]
    by_id = {item["id"]: item for item in items}
    results = []
    for result in rank(parsed, items, body.broaden):
        item = by_id[result["id"]]
        results.append({**result,
                        **{field: item[field] for field in ("category", "color", "brand", "location", "mark")},
                        "photo_url": f"/api/items/{result['id']}/photo",
                        "coverage_text": f"{result['coverage']} of 5 attributes supplied",
                        "match_label": "Related suggestion, different category" if result["related"] else "Candidate match"})
    return {"parsed": parsed, "results": results, "clarification": None,
            "message": None if results else "No matching available items. Try different details or explicitly include related categories."}
