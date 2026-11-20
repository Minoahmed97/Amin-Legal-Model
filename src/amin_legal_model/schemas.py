from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class LegalRequest(BaseModel):
    task: str = Field(
        description="One of: analyze, deconstruct, qualify, draft, consult.",
        min_length=1,
        max_length=40,
    )
    text: str = Field(min_length=1, max_length=100_000)
    jurisdiction: str = "EG"
    language: str = "ar"
    retrieval_query: str | None = Field(default=None, max_length=2_000)
    as_of_date: date | None = None


class LegalResponse(BaseModel):
    status: str
    answer: str | None = None
    sources: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StrategyPoint(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    supported_by_record: bool = False
    materiality: Literal["critical", "high", "medium", "low"] = "medium"


class LegalStrategyRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=2_000)
    case_stage: str = Field(min_length=1, max_length=200)
    client_role: str = Field(min_length=1, max_length=200)
    as_of_date: date = Field(default_factory=date.today)
    deadline_date: date | None = None
    deadline_verified: bool = False
    mandatory_response: bool = False
    silence_harm_possible: bool = False
    risk_of_curative_reply: bool = False
    request_full_brief: bool = False
    opponent_points: list[StrategyPoint] = Field(default_factory=list, max_length=30)
    response_points: list[StrategyPoint] = Field(default_factory=list, max_length=30)
    missing_documents: list[str] = Field(default_factory=list, max_length=50)
