"""B04 registration and explicitly allowlisted public item views."""
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from ..ai.vocabulary import VOCAB
from ..auth import require_staff
from ..database import connect
from ..services import images

router = APIRouter()
PUBLIC_SELECT = """SELECT i.id,i.category,i.color,i.brand,i.location,i.status,i.created_at,
 a.value AS mark FROM items i LEFT JOIN item_attributes a
 ON a.item_id=i.id AND a.name='mark' AND a.private=0"""


def canonical(field, value, required=True):
    value = value.strip() if value is not None else ""
    if not value and not required:
        return None
    if len(value) > 500 or value not in VOCAB[field]:
        raise HTTPException(422, f"{field} must be a canonical value: {', '.join(VOCAB[field])}")
    return value


def public_item(row):
    return {**dict(row), "photo_url": f"/api/items/{row['id']}/photo"}


@router.post("/api/items", status_code=201, dependencies=[Depends(require_staff)])
def create_item(
    event_id: Annotated[str, Form()],
    category: Annotated[str, Form()],
    color: Annotated[str, Form()],
    location: Annotated[str, Form()],
    photo: Annotated[UploadFile, File()],
    brand: Annotated[str | None, Form()] = None,
    mark: Annotated[str | None, Form()] = None,
    private_mark: Annotated[str | None, Form()] = None,
):
    event_id = event_id.strip()
    if not event_id or len(event_id) > 80:
        raise HTTPException(422, "event_id must contain 1-80 characters")
    category = canonical("category", category)
    color = canonical("color", color)
    location = canonical("location", location)
    brand = canonical("brand", brand, required=False)
    mark = canonical("mark", mark, required=False)
    private_mark = (private_mark or "").strip()
    if len(private_mark) > 500:
        raise HTTPException(422, "private_mark exceeds 500 characters")
    with connect() as db:
        if not db.execute("SELECT 1 FROM device_events WHERE event_id=?", (event_id,)).fetchone():
            raise HTTPException(404, "Event not found")
        if db.execute("SELECT 1 FROM items WHERE event_id=?", (event_id,)).fetchone():
            raise HTTPException(409, "Event already registered")
    # Expensive image work stays outside the database write transaction.
    jpeg = images.sanitize(photo.file)
    name = images.save_photo(jpeg)
    try:
        with connect() as db:
            cursor = db.execute(
                "INSERT INTO items(event_id,category,color,brand,location,photo_path) VALUES(?,?,?,?,?,?)",
                (event_id, category, color, brand, location, name),
            )
            item_id = cursor.lastrowid
            for attribute, value, private in [("mark", mark, 0), ("private_mark", private_mark, 1)]:
                if value:
                    db.execute("INSERT INTO item_attributes(item_id,name,value,private) VALUES(?,?,?,?)",
                               (item_id, attribute, value, private))
    except Exception as error:
        images.photo_path(name).unlink(missing_ok=True)
        if isinstance(error, sqlite3.IntegrityError):
            # A concurrent registration can win after the preflight check.
            with connect() as db:
                if db.execute("SELECT 1 FROM items WHERE event_id=?", (event_id,)).fetchone():
                    raise HTTPException(409, "Event already registered") from None
                if not db.execute("SELECT 1 FROM device_events WHERE event_id=?", (event_id,)).fetchone():
                    raise HTTPException(404, "Event not found") from None
        raise
    return {"id": item_id, "status": "available", "event_id": event_id}


@router.get("/api/items")
def list_items(limit: Annotated[int, Query(ge=1, le=50)] = 20,
               offset: Annotated[int, Query(ge=0)] = 0):
    with connect() as db:
        rows = db.execute(PUBLIC_SELECT + " WHERE i.status='available' ORDER BY i.id LIMIT ? OFFSET ?",
                          (limit + 1, offset)).fetchall()
    return {"items": [public_item(row) for row in rows[:limit]],
            "next_offset": offset + limit if len(rows) > limit else None}


@router.get("/api/items/{item_id}")
def get_item(item_id: int):
    with connect() as db:
        row = db.execute(PUBLIC_SELECT + " WHERE i.id=? AND i.status='available'", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Available item not found")
    return public_item(row)


@router.get("/api/items/{item_id}/photo")
def get_photo(item_id: int):
    with connect() as db:
        row = db.execute("SELECT photo_path FROM items WHERE id=? AND status='available'", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Available item not found")
    try:
        jpeg = images.photo_path(row["photo_path"]).read_bytes()
    except FileNotFoundError:
        raise HTTPException(404, "Photo not found") from None
    return Response(jpeg, media_type="image/jpeg", headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
