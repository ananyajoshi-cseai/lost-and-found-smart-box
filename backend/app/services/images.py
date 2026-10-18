"""Decode untrusted uploads and retain only newly encoded JPEG pixels."""
import io
import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 12_000_000


def upload_directory():
    return Path(os.getenv("UPLOAD_DIR") or "uploads").resolve()


def photo_path(name):
    # Database filenames are server-generated too; never interpret arbitrary paths.
    if not re.fullmatch(r"[0-9a-f]{32}\.jpg", name):
        raise HTTPException(404, "Photo not found")
    root = upload_directory()
    candidate = (root / name).resolve()
    if candidate.parent != root:
        raise HTTPException(404, "Photo not found")
    return candidate


def sanitize(stream):
    payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise HTTPException(413, "Photo exceeds 5 MiB")
    try:
        with Image.open(io.BytesIO(payload)) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise HTTPException(422, "Photo must be a decoded JPEG or PNG")
            if image.width * image.height > MAX_PIXELS:
                raise HTTPException(413, "Photo exceeds 12 megapixels")
            image.verify()
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            oriented = ImageOps.exif_transpose(image)
            # A fresh image copies pixels only, never EXIF, comments or PNG text.
            rgb = oriented.convert("RGB")
            clean = Image.new("RGB", rgb.size)
            clean.paste(rgb)
            output = io.BytesIO()
            clean.save(output, format="JPEG", quality=90)
            return output.getvalue()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(413, "Photo dimensions are too large") from None
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise HTTPException(422, "Photo is invalid or damaged") from None


def save_photo(jpeg):
    root = upload_directory()
    root.mkdir(parents=True, exist_ok=True)
    name = uuid4().hex + ".jpg"
    path = root / name
    try:
        with path.open("xb") as target:
            target.write(jpeg)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return name


def audit_storage():
    """Read-only recovery report; run while the server is stopped."""
    from ..database import connect
    with connect() as db:
        referenced = {row["photo_path"] for row in db.execute("SELECT photo_path FROM items")}
    present = {path.name for path in upload_directory().glob("*.jpg")}
    return {"unreferenced": sorted(present - referenced), "missing": sorted(referenced - present)}


if __name__ == "__main__":
    import json
    print(json.dumps(audit_storage(), indent=2))
