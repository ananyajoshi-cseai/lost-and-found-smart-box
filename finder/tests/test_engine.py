import pytest
from finder_core.engine import parse, bfs, rank

ITEM = dict(id=101, category="bottle", color="blue", brand="milton", location="library", mark="star", status="available")

@pytest.mark.parametrize("text,expected", [
 ("navy flask", {"category":"bottle","color":"blue"}),
 ("I misplaced my dark blue Milton water bottle near the library.", {"category":"bottle","color":"blue","brand":"milton","location":"library"}),
 ("Miltn bottle", {"category":"bottle"}),
 ("something lost", {})])
def test_parse(text, expected):
 assert parse(text)["positive"] == expected

@pytest.mark.parametrize("text", ["bottle not blue", "not dark blue bottle", "bottle without navy", "bottle no blue"])
def test_negation(text):
 q=parse(text)
 assert q["excluded"] == {"color":["blue"]}
 assert rank(q,[ITEM]) == []

@pytest.mark.parametrize("text", ["red blue bottle", "blue not blue bottle"])
def test_ambiguity(text):
 q=parse(text)
 assert "color" in q["ambiguous"]
 assert rank(q,[ITEM]) == []

def test_score_arithmetic_and_strong_rule():
 r=rank(parse("blue milton bottle canteen star"),[ITEM])[0]
 assert r["score"] == 90
 assert r["coverage"] == 5 and r["strong_candidate"]
 assert sum(r["reasons"].values()) == 90
 assert rank(parse("blue milton bottle canteen"),[ITEM])[0]["score"] == 88.89

def test_omitted_fields_and_missing_values():
 assert rank(parse("bottle"),[ITEM])[0]["score"] == 100
 assert rank(parse("bottle"),[ITEM])[0]["coverage"] == 1
 assert rank(parse("blue milton bottle"),[{**ITEM,"brand":None}])[0]["score"] == 81.25

def test_availability_ties_and_top_three():
 assert rank(parse("bottle"),[{**ITEM,"status":"returned"}]) == []
 assert [r["id"] for r in rank(parse("bottle"),[{**ITEM,"id":i} for i in [8,4,3,2]])] == [2,3,4]

def test_bfs_and_related_fallback():
 assert bfs("bottle") == {"bottle":0,"personalitems":1,"campusitem":2,"umbrella":2,"keys":2}
 assert bfs("missing") == {}
 assert bfs("bottle",0) == {"bottle":0}
 related={**ITEM,"category":"umbrella"}
 assert rank(parse("bottle"),[related],True) == []
 assert rank(parse("blue milton bottle library star"),[related]) == []
 r=rank(parse("blue milton bottle library star"),[related],True)[0]
 assert r["related"] and r["score"] == 60 and not r["strong_candidate"]
 poor={**ITEM,"color":"red","brand":None,"mark":None,"location":"canteen"}
 assert rank(parse("blue milton bottle library star"),[poor,related],True) == []

def test_empty_query():
 assert rank(parse("something"),[ITEM]) == []
