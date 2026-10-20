from .parser import parse
from .ontology import bfs
from .scoring import rank as _rank


def rank(query, items, broaden=False):
    """Proposal contract, with coverage retained for honest score interpretation."""
    return [{**r, "reasons": {part["field"]: part["points"] for part in r["reasons"]},
             "coverage_text": f"{r['coverage']} of 5 attributes supplied"}
            for r in _rank(query, items, broaden)]
