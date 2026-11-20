from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LegalSource:
    title: str
    text: str
    source_url: str | None = None
    source_type: str = "unverified"
    jurisdiction: str = "EG"
    effective_date: str | None = None


class LegalRetriever(Protocol):
    async def search(self, query: str, *, limit: int = 5) -> list[LegalSource]:
        """Return source passages with provenance; never fabricate citations."""
        ...
