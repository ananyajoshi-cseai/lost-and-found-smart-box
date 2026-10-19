"""Offline database + photo bundles; restore only into a new directory."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3

PHOTO_NAME = re.compile(r"[0-9a-f]{32}\.jpg")
TABLES = {"device_events", "items", "item_attributes", "claim_requests", "claim_audit"}


def readonly(path):
    return sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True, timeout=5)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect_database(path):
    with closing(readonly(path)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("Database integrity check failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Database contains broken foreign keys")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not TABLES <= tables:
            raise ValueError("Not a Smart Box database")
        photos = {row[0] for row in db.execute("SELECT photo_path FROM items")}
        if any(not isinstance(name, str) or not PHOTO_NAME.fullmatch(name) for name in photos):
            raise ValueError("Database contains an unsafe photo filename")
        counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in sorted(TABLES)}
        return photos, counts


def safe_file(root, relative):
    root = Path(root).resolve()
    path = root / relative
    if path.is_symlink() or path.resolve() != path.absolute() or not path.is_file():
        raise ValueError(f"Missing or linked bundle file: {relative}")
    if root not in path.resolve().parents:
        raise ValueError("File escapes the bundle directory")
    return path


def backup(database, uploads, destination, *, server_stopped=False):
    if not server_stopped:
        raise ValueError("Stop the server before backing up database and photos together")
    database, uploads, destination = Path(database).resolve(), Path(uploads).resolve(), Path(destination).absolute()
    if not database.is_file():
        raise ValueError("Source database does not exist")
    # Never overwrite a prior backup; incomplete runs have no manifest.
    destination.mkdir(parents=False, exist_ok=False)
    target_db = destination / "smartbox.db"
    with closing(readonly(database)) as source, closing(sqlite3.connect(target_db)) as target:
        source.backup(target)
    photos, counts = inspect_database(target_db)
    (destination / "uploads").mkdir()
    for name in sorted(photos):
        source = safe_file(uploads, name)
        shutil.copyfile(source, destination / "uploads" / name)
    files = {"smartbox.db": digest(target_db)}
    files.update({"uploads/" + name: digest(destination / "uploads" / name) for name in sorted(photos)})
    manifest = {"format_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "files": files, "row_counts": counts}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify(bundle):
    bundle = Path(bundle).resolve()
    manifest = json.loads(safe_file(bundle, "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("format_version") != 1 or not isinstance(manifest.get("files"), dict):
        raise ValueError("Unsupported or incomplete backup manifest")
    files = manifest["files"]
    if "smartbox.db" not in files:
        raise ValueError("Backup lacks database")
    for relative, checksum in files.items():
        if relative != "smartbox.db" and not re.fullmatch(r"uploads/[0-9a-f]{32}\.jpg", relative):
            raise ValueError("Unsafe manifest filename")
        if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise ValueError("Invalid checksum")
        if digest(safe_file(bundle, relative)) != checksum:
            raise ValueError(f"Checksum mismatch: {relative}")
    photos, counts = inspect_database(bundle / "smartbox.db")
    if set(files) != {"smartbox.db"} | {"uploads/" + name for name in photos}:
        raise ValueError("Manifest photo references do not match database")
    if counts != manifest.get("row_counts"):
        raise ValueError("Manifest row counts do not match database")
    return manifest


def restore(bundle, destination):
    manifest = verify(bundle)
    bundle, destination = Path(bundle).resolve(), Path(destination).absolute()
    destination.mkdir(parents=False, exist_ok=False)
    (destination / "uploads").mkdir()
    for relative, checksum in manifest["files"].items():
        target = destination / relative
        shutil.copyfile(safe_file(bundle, relative), target)
        if digest(target) != checksum:
            raise ValueError("Copy verification failed; do not use this incomplete restore")
    inspect_database(destination / "smartbox.db")
    # Marker is written last. Do not run the app on a copy missing this marker.
    (destination / "RESTORE_COMPLETE.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    save = sub.add_parser("backup")
    save.add_argument("--database", type=Path, required=True)
    save.add_argument("--uploads", type=Path, required=True)
    save.add_argument("--destination", type=Path, required=True)
    save.add_argument("--server-stopped", action="store_true")
    check = sub.add_parser("verify")
    check.add_argument("bundle", type=Path)
    recover = sub.add_parser("restore")
    recover.add_argument("bundle", type=Path)
    recover.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "backup":
            backup(args.database,args.uploads,args.destination,server_stopped=args.server_stopped)
            print("Backup completed and manifest written.")
        elif args.command == "verify":
            verify(args.bundle)
            print("Database, referenced photos and checksums verified.")
        else:
            restore(args.bundle,args.destination)
            print("Restore verified in the new directory. Original files were not changed.")
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Recovery operation failed: {error}\n")


if __name__ == "__main__":
    main()
