from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class EventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    device_id: str = Field(min_length=1, max_length=40)
    kind: Literal["deposit"]


class SearchIn(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    broaden: bool = False


class ParsedQuery(BaseModel):
    positive: dict[str, str]
    excluded: dict[str, list[str]]
    ambiguous: list[str]


class ScoreReason(BaseModel):
    field: str
    weight: int
    points: int
    matched: bool


class SearchResult(BaseModel):
    id: int
    score: float
    coverage: int
    denominator: int
    reasons: list[ScoreReason]
    strong_candidate: bool
    related: bool
    category: str
    color: str
    brand: str | None
    location: str
    mark: str | None
    photo_url: str
    coverage_text: str
    match_label: str


class SearchOut(BaseModel):
    parsed: ParsedQuery
    results: list[SearchResult]
    clarification: str | None
    message: str | None
