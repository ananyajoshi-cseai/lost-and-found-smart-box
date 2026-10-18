import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connect():
    db = sqlite3.connect(os.getenv("DATABASE_PATH", "smartbox.db"), timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize():
    with connect() as db:
        db.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))


if __name__ == "__main__":
    initialize()
    print("Database schema initialized.")
