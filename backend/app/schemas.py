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
