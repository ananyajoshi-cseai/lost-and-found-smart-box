from fastapi import APIRouter, Depends, HTTPException, Response
from ..auth import require_device, require_staff
from ..database import connect
from ..schemas import EventIn

router = APIRouter()


@router.post("/api/device/events", status_code=201, dependencies=[Depends(require_device)])
def create_event(event: EventIn, response: Response):
    with connect() as db:
        inserted = db.execute("INSERT INTO device_events(event_id,device_id,kind) VALUES(?,?,?) ON CONFLICT(event_id) DO NOTHING",
                              (event.event_id, event.device_id, event.kind)).rowcount
        row = db.execute("SELECT * FROM device_events WHERE event_id=?", (event.event_id,)).fetchone()
        if row["device_id"] != event.device_id or row["kind"] != event.kind:
            raise HTTPException(409, "Event ID already represents a different payload")
        response.status_code = 201 if inserted else 200
        return {**dict(row), "duplicate": not bool(inserted)}


@router.get("/api/admin/events", dependencies=[Depends(require_staff)])
def pending_events(pending: bool = True):
    with connect() as db:
        sql = "SELECT e.* FROM device_events e"
        if pending:
            sql += " WHERE NOT EXISTS (SELECT 1 FROM items i WHERE i.event_id=e.event_id)"
        return {"events": [dict(row) for row in db.execute(sql + " ORDER BY e.created_at,e.event_id")]}
