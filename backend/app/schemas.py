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


class ClaimIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    item_id: int = Field(gt=0, strict=True)
    contact: str = Field(min_length=1, max_length=120)
    evidence: str = Field(min_length=1, max_length=500)


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reason: str = Field(min_length=1, max_length=500)


class ClaimReceipt(BaseModel):
    claim_id: int
    status: Literal["pending"]


class ApprovalOut(BaseModel):
    claim_id: int
    status: Literal["approved"]
    item_status: Literal["claimed"]


class RejectionOut(BaseModel):
    claim_id: int
    status: Literal["rejected"]


class AuditEntry(BaseModel):
    actor: str
    action: Literal["approved", "rejected"]
    reason: str
    created_at: str


class StaffClaim(BaseModel):
    claim_id: int
    item_id: int
    contact: str
    evidence: str
    status: Literal["pending", "approved", "rejected"]
    created_at: str
    item_status: Literal["available", "claimed"]
    private_mark: str | None
    audit: list[AuditEntry]


class StaffClaimsOut(BaseModel):
    claims: list[StaffClaim]
