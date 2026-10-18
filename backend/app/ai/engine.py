"""Stable facade for handbook examples."""
from .parser import parse
from .ontology import bfs
from .scoring import rank

__all__ = ["parse", "bfs", "rank"]
