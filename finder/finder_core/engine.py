from .parser import parse, suggest_corrections, apply_correction
from .ontology import bfs
from .scoring import rank as _rank
from .vague_matching import match_vague_description

def parse_with_vague_matching(text):
    """Parse normal attributes and detect vague item descriptions."""

    parsed = parse(text)

    # Only look for vague descriptions if category is not already known.
    if "category" not in parsed["positive"]:
        matches = match_vague_description(text)

        if len(matches) == 1:
            parsed["positive"]["category"] = matches[0]

        elif len(matches) > 1:
            parsed["ambiguous"].append("category")

    return parsed

def rank(query, items, broaden=False):
    """Proposal contract, with coverage retained for honest score interpretation."""
    return [{**r, "reasons": {part["field"]: part["points"] for part in r["reasons"]},
             "coverage_text": f"{r['coverage']} of 5 attributes supplied"}
            for r in _rank(query, items, broaden)]
