import os
import pytest
from app.ai.engine import parse, rank
from app.database import connect
from evaluation import isolated_client, load_dataset, summarize, timing_summary


def test_metrics_count_queries_not_cards_and_include_misses():
    runs = [
        {"kind":"positive", "relevant_ids":[1,2], "returned_ids":[1,2,3]},
        {"kind":"positive", "relevant_ids":[4], "returned_ids":[7,4,8]},
        {"kind":"positive", "relevant_ids":[9], "returned_ids":[]},
        {"kind":"negative", "relevant_ids":[], "returned_ids":[3,4,5]},
        {"kind":"negative", "relevant_ids":[], "returned_ids":[]},
    ]
    result = summarize(runs)
    assert result["top1_hits"] == 1 and result["top3_hits"] == 2
    assert result["top1_accuracy"] == 1/3 and result["top3_success"] == 2/3
    assert result["negative_false_positive_rate"] == 1/2
    assert summarize([])["top1_accuracy"] is None
    assert summarize([])["negative_false_positive_rate"] is None


def test_timing_nearest_rank_and_empty_guard():
    assert timing_summary(list(range(1,101))) == {"samples":100,"median_ms":50.5,"p95_ms":95,"max_ms":100}
    with pytest.raises(ValueError):
        timing_summary([])


def test_fixture_labels_and_environment_isolation(monkeypatch, tmp_path):
    items, queries = load_dataset()
    assert len(items) == 20
    assert sum(q["kind"] == "positive" for q in queries) >= 10
    assert sum(q["kind"] == "negative" for q in queries) >= 5
    sentinel = tmp_path / "keep.db"
    sentinel.write_bytes(b"never open this database")
    monkeypatch.setenv("DATABASE_PATH", str(sentinel))
    with pytest.raises(RuntimeError, match="test interruption"):
        with isolated_client(items):
            assert os.environ["DATABASE_PATH"] != str(sentinel)
            raise RuntimeError("test interruption")
    assert os.environ["DATABASE_PATH"] == str(sentinel)
    assert sentinel.read_bytes() == b"never open this database"


def test_live_search_agrees_with_ranker_and_redacts_private_fields():
    items, queries = load_dataset()
    with isolated_client(items) as client:
        for query in queries:
            response = client.post("/api/search", json={"query":query["query"], "broaden":query["broaden"]})
            assert response.status_code == 200
            result = response.json()
            expected = rank(parse(query["query"]), items, query["broaden"])
            assert [r["id"] for r in result["results"]] == [r["id"] for r in expected]
            for actual, ranked in zip(result["results"], expected):
                assert all(actual[key] == value for key,value in ranked.items())
                assert actual["coverage_text"] == f"{actual['coverage']} of 5 attributes supplied"
                assert actual["match_label"] == ("Related suggestion, different category" if actual["related"] else "Candidate match")
                assert client.get(actual["photo_url"]).status_code == 200
                assert set(actual) == {"id","score","coverage","denominator","reasons","strong_candidate","related","category","color","brand","location","mark","photo_url","coverage_text","match_label"}
            assert "SYNTHETIC_PRIVATE_SENTINEL" not in response.text
            assert "private_mark" not in response.text and "photo_path" not in response.text
            if not result["results"]:
                assert result["message"]
        with connect() as db:
            db.execute("UPDATE item_attributes SET private=1 WHERE name='mark'")
        result = client.post("/api/search",json={"query":"blue bottle"}).json()
        assert all(r["mark"] is None for r in result["results"])


def test_empty_pool_and_validation():
    with isolated_client([]) as client:
        result = client.post("/api/search",json={"query":"bottle"}).json()
        assert result["results"] == [] and result["clarification"] is None
        assert result["message"].startswith("No matching available items")
        for value in ["", "x"*301]:
            assert client.post("/api/search",json={"query":value}).status_code == 422
        assert client.post("/api/search",json={"query":"red blue bottle"}).json()["clarification"]
