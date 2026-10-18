import io
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from PIL import Image, PngImagePlugin
from app.main import app
from app.database import connect
from app.services import images

AUTH = ("test-staff", "test-password")
FIELDS = {"event_id": "box01-item-1", "category": "bottle", "color": "blue",
          "location": "library", "brand": "milton", "mark": "star", "private_mark": "HIDDEN INITIALS"}

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("DEVICE_KEY", "test-device")
    monkeypatch.setenv("STAFF_USERNAME", AUTH[0])
    monkeypatch.setenv("STAFF_PASSWORD", AUTH[1])
    with TestClient(app) as client:
        yield client


def photo(format="PNG", size=(20, 30)):
    data = io.BytesIO()
    image = Image.new("RGB", size, "blue")
    if format == "PNG":
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("private", "HIDDEN METADATA")
        image.save(data, format=format, pnginfo=metadata)
    else:
        image.save(data, format=format)
    return data.getvalue()


def event(client, event_id=FIELDS["event_id"]):
    assert client.post("/api/device/events", headers={"X-Device-Key": "test-device"},
                       json={"event_id": event_id, "device_id": "box01", "kind": "deposit"}).status_code == 201


def register(client, fields=None, payload=None, auth=AUTH):
    return client.post("/api/items", data=FIELDS if fields is None else fields, auth=auth,
                       files={"photo": ("../../unsafe.png", photo() if payload is None else payload, "image/png")})


def test_event_registration_search_photo_flow(client):
    event(client)
    created = register(client)
    assert created.status_code == 201
    result = created.json()
    item_id = result["id"]
    assert result == {"id": item_id, "event_id": FIELDS["event_id"], "status": "available"}
    assert client.get("/api/admin/events", auth=AUTH).json() == {"events": []}
    detail = client.get(f"/api/items/{item_id}")
    assert detail.json()["mark"] == "star"
    assert detail.json()["photo_url"] == f"/api/items/{item_id}/photo"
    listing = client.get("/api/items").json()
    assert listing == {"items": [detail.json()], "next_offset": None}
    search = client.post("/api/search", json={"query": "navy milton flask star"})
    assert search.json()["results"][0]["id"] == item_id
    for response in (detail, search, client.get("/api/items")):
        assert "HIDDEN" not in response.text and "private_mark" not in response.text
        assert "photo_path" not in response.text and "event_id" not in response.text
    served = client.get(detail.json()["photo_url"])
    assert served.status_code == 200 and served.headers["content-type"] == "image/jpeg"
    assert served.headers["cache-control"] == "no-store"
    with Image.open(io.BytesIO(served.content)) as image:
        assert image.format == "JPEG" and image.mode == "RGB" and image.size == (20, 30)
        assert not image.getexif() and "private" not in image.info
    assert b"HIDDEN" not in served.content
    assert len(list(images.upload_directory().glob("*.jpg"))) == 1
    with TestClient(app) as restarted:
        assert restarted.get(f"/api/items/{item_id}/photo").content == served.content
    with connect() as db:
        assert db.execute("SELECT value FROM item_attributes WHERE private=1").fetchone()[0] == "HIDDEN INITIALS"
        db.execute("UPDATE items SET status='claimed' WHERE id=?", (item_id,))
    assert client.get(f"/api/items/{item_id}").status_code == 404
    assert client.get(f"/api/items/{item_id}/photo").status_code == 404
    assert client.get("/api/items").json()["items"] == []
    assert client.post("/api/search", json={"query": "bottle"}).json()["results"] == []


def test_auth_missing_event_and_duplicate(client):
    assert register(client, auth=None).status_code == 401
    assert register(client, auth=("bad", "bad")).status_code == 401
    assert register(client).status_code == 404
    event(client)
    assert register(client).status_code == 201
    assert register(client).status_code == 409
    assert len(list(images.upload_directory().glob("*.jpg"))) == 1


@pytest.mark.parametrize("field,value", [("category", "flask"), ("color", "navy"), ("brand", "unknown"),
    ("location", "moon"), ("mark", "x"*501), ("private_mark", "x"*501), ("category", " "), ("event_id", "x"*81)])
def test_invalid_fields(client, field, value):
    event(client)
    assert register(client, {**FIELDS, field: value}).status_code == 422
    assert not images.upload_directory().exists()


@pytest.mark.parametrize("payload,status", [(b"<svg>not a photo</svg>", 422), (b"", 422),
    (b"x" * (images.MAX_BYTES + 1), 413)], ids=["svg", "empty", "oversized"])
def test_invalid_image_keeps_event_pending(client, payload, status):
    event(client)
    assert register(client, payload=payload).status_code == status
    assert len(client.get("/api/admin/events", auth=AUTH).json()["events"]) == 1
    assert not images.upload_directory().exists()


def test_format_pixels_truncation_and_jpeg(client):
    event(client)
    assert register(client, payload=photo("GIF")).status_code == 422
    assert register(client, payload=photo(size=(4000, 3001))).status_code == 413
    assert register(client, payload=photo()[:30]).status_code == 422
    assert register(client, payload=photo("JPEG")).status_code == 201


def test_optional_fields_trim_and_missing_photo(client):
    event(client)
    fields = {k: " " + v + " " for k, v in FIELDS.items() if k not in {"brand", "mark", "private_mark"}}
    assert client.post("/api/items", data=fields, auth=AUTH).status_code == 422
    result = register(client, fields)
    assert result.status_code == 201
    detail = client.get(f"/api/items/{result.json()['id']}").json()
    assert detail["brand"] is None and detail["mark"] is None


def test_pagination_and_unknown_ids(client):
    for i in range(3):
        event_id = f"page-{i}"
        event(client, event_id)
        assert register(client, {**FIELDS, "event_id": event_id}).status_code == 201
    page = client.get("/api/items?limit=2").json()
    assert len(page["items"]) == 2 and page["next_offset"] == 2
    last = client.get("/api/items?limit=2&offset=2").json()
    assert len(last["items"]) == 1 and last["next_offset"] is None
    assert page["items"][1]["id"] < last["items"][0]["id"]
    for query in ("limit=0", "limit=51", "offset=-1"):
        assert client.get("/api/items?"+query).status_code == 422
    assert client.get("/api/items/99999").status_code == 404
    assert client.get("/api/items/99999/photo").status_code == 404


def test_transaction_failure_removes_orphan_and_rolls_back(client):
    event(client)
    with connect() as db:
        db.execute("CREATE TRIGGER fail_attribute BEFORE INSERT ON item_attributes BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
    response = register(client)
    assert response.status_code == 500 and response.json() == {"detail": "Database operation failed"}
    assert not list(images.upload_directory().glob("*.jpg"))
    with connect() as db:
        assert db.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM item_attributes").fetchone()[0] == 0
    assert len(client.get("/api/admin/events", auth=AUTH).json()["events"]) == 1


def test_concurrent_registration_only_one_item_and_photo(client, monkeypatch):
    event(client)
    barrier = Barrier(2)
    original = images.save_photo
    def coordinated_save(jpeg):
        name = original(jpeg)
        barrier.wait(timeout=10)
        return name
    monkeypatch.setattr(images, "save_photo", coordinated_save)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: register(client), range(2)))
    assert sorted(r.status_code for r in responses) == [201, 409]
    assert len(list(images.upload_directory().glob("*.jpg"))) == 1
    assert len(client.get("/api/items").json()["items"]) == 1


def test_untrusted_stored_path_and_missing_photo(client):
    event(client)
    result = register(client).json()
    with connect() as db:
        name = db.execute("SELECT photo_path FROM items").fetchone()[0]
    images.photo_path(name).unlink()
    assert client.get(f"/api/items/{result['id']}/photo").status_code == 404
    with connect() as db:
        db.execute("UPDATE items SET photo_path='../secret.jpg'")
    assert client.get(f"/api/items/{result['id']}/photo").status_code == 404


def test_storage_audit_is_read_only(client):
    event(client)
    register(client)
    with connect() as db:
        name = db.execute("SELECT photo_path FROM items").fetchone()[0]
    orphan = images.save_photo(photo("JPEG"))
    images.photo_path(name).unlink()
    assert images.audit_storage() == {"unreferenced": [orphan], "missing": [name]}
    assert images.photo_path(orphan).exists()
