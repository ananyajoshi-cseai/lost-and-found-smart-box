"""Reproducible synthetic evaluation through the real API, isolated from demo data."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
from time import perf_counter

from fastapi.testclient import TestClient
from PIL import Image
from app.database import connect
from app.main import app

BASE = Path(__file__).resolve().parent
FIXTURES = BASE / "tests" / "fixtures"


def load_dataset():
    items = json.loads((FIXTURES / "items.json").read_text(encoding="utf-8"))
    queries = json.loads((FIXTURES / "queries.json").read_text(encoding="utf-8"))
    ids = {item["id"] for item in items}
    if len(ids) != len(items):
        raise ValueError("Duplicate item IDs")
    if len({q["id"] for q in queries}) != len(queries):
        raise ValueError("Duplicate query IDs")
    for q in queries:
        if q["kind"] not in {"positive", "negative"}:
            raise ValueError("Invalid query kind")
        if (q["kind"] == "positive") != bool(q["relevant_ids"]):
            raise ValueError("Label kind disagrees with relevant IDs")
        if not set(q["relevant_ids"]) <= ids:
            raise ValueError("Unknown labelled item")
    return items, queries


@contextmanager
def isolated_client(items):
    # Restore the caller's configuration even if a test/evaluation fails.
    with tempfile.TemporaryDirectory(prefix="smartbox-eval-") as directory:
        root = Path(directory)
        config = {"DATABASE_PATH": str(root / "evaluation.db"), "UPLOAD_DIR": str(root / "uploads"),
                  "DEVICE_KEY": "synthetic-evaluation", "STAFF_USERNAME": "synthetic",
                  "STAFF_PASSWORD": "synthetic-evaluation-only"}
        previous = {key: os.environ.get(key) for key in config}
        os.environ.update(config)
        try:
            with TestClient(app) as client:
                uploads = root / "uploads"
                uploads.mkdir()
                with connect() as db:
                    for item in items:
                        event_id = f"eval-{item['id']}"
                        name = f"{item['id']:032x}.jpg"
                        Image.new("RGB", (8, 8), item["color"]).save(uploads / name, "JPEG")
                        db.execute("INSERT INTO device_events(event_id,device_id,kind) VALUES(?,?,'deposit')", (event_id,"evaluation"))
                        db.execute("INSERT INTO items(id,event_id,category,color,brand,location,photo_path,status) VALUES(?,?,?,?,?,?,?,?)",
                                   (item["id"],event_id,item["category"],item["color"],item["brand"],item["location"],name,item["status"]))
                        if item.get("mark") is not None:
                            db.execute("INSERT INTO item_attributes VALUES(?,?,?,0)",(item["id"],"mark",item["mark"]))
                        db.execute("INSERT INTO item_attributes VALUES(?,?,?,1)",(item["id"],"private_mark","SYNTHETIC_PRIVATE_SENTINEL"))
                yield client
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def summarize(runs):
    positive = [r for r in runs if r["kind"] == "positive"]
    negative = [r for r in runs if r["kind"] == "negative"]
    top1 = sum(bool(r["returned_ids"]) and r["returned_ids"][0] in r["relevant_ids"] for r in positive)
    top3 = sum(bool(set(r["returned_ids"][:3]) & set(r["relevant_ids"])) for r in positive)
    false_positive = sum(bool(r["returned_ids"]) for r in negative)
    return {"positive_queries": len(positive), "negative_queries": len(negative),
            "top1_hits": top1, "top3_hits": top3, "negative_false_positives": false_positive,
            "top1_accuracy": top1 / len(positive) if positive else None,
            "top3_success": top3 / len(positive) if positive else None,
            "negative_false_positive_rate": false_positive / len(negative) if negative else None}


def timing_summary(values):
    if not values:
        raise ValueError("No timing samples")
    ordered = sorted(values)
    return {"samples": len(values), "median_ms": statistics.median(values),
            "p95_ms": ordered[math.ceil(0.95 * len(values)) - 1], "max_ms": max(values)}


def search(client, query):
    # Labels and intended IDs are never sent to application code.
    start = perf_counter()
    response = client.post("/api/search", json={"query": query["query"], "broaden": query["broaden"]})
    elapsed = (perf_counter() - start) * 1000
    response.raise_for_status()
    return response.json(), elapsed


def evaluate(repeats=10):
    if repeats < 1:
        raise ValueError("repeats must be positive")
    items, queries = load_dataset()
    runs = []
    with isolated_client(items) as client:
        for query in queries:
            result, elapsed = search(client, query)
            runs.append({**query, "returned_ids": [r["id"] for r in result["results"]],
                         "response": result, "elapsed_ms": elapsed})
    # 100 available rows force the retrieval path to inspect the full benchmark pool.
    benchmark_items = [{**items[i % len(items)], "id": 1001+i, "status": "available"} for i in range(100)]
    benchmark_queries = [q for q in queries if q["kind"] == "positive"]
    timings = []
    with isolated_client(benchmark_items) as client:
        for query in benchmark_queries:
            search(client, query)  # one unmeasured warm-up per query
        for repeat in range(repeats):
            for query in benchmark_queries:
                _, elapsed = search(client, query)
                timings.append({"repeat": repeat+1, "query_id": query["id"], "ms": elapsed})
    paths = [FIXTURES / "items.json", FIXTURES / "queries.json", BASE / "evaluation.py", BASE / "requirements.txt"]
    paths += sorted((BASE / "app").rglob("*.py"))
    hashes = {str(path.relative_to(BASE)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=BASE, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    latency = timing_summary([r["ms"] for r in timings])
    return {"dataset_version": "synthetic-v1", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": commit, "working_tree_dirty": dirty, "sha256": hashes,
            "machine": {"os": platform.platform(), "python": platform.python_version(),
                        "processor": platform.processor(), "logical_cpus": os.cpu_count()},
            "item_count": len(items), "metrics": summarize(runs), "query_runs": runs,
            "benchmark": {"item_count": 100, "available_count": 100, "repeats": repeats,
                          "method": "In-process FastAPI TestClient: request serialization, SQLite read, parse/rank, response validation. No browser/network/photo-download time; warm-up excluded; p95 nearest rank.",
                          **latency, "all_samples_under_500_ms": latency["max_ms"] < 500, "timings": timings}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new filename to preserve previous evidence")
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    report = evaluate(args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")
    print(json.dumps({"metrics": report["metrics"], "benchmark": {k:v for k,v in report["benchmark"].items() if k != "timings"}}, indent=2))


if __name__ == "__main__":
    main()
