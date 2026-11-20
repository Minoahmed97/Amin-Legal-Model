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


class LegalResponse(BaseModel):
    status: str
    answer: str | None = None
    sources: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
