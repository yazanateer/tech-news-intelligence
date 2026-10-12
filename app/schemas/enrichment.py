from typing import List

from pydantic import BaseModel, Field, field_validator

MAX_TAGS = 3


class EnrichmentResult(BaseModel):
    """Validated shape of the AI enrichment returned by the LLM."""

    category: str = Field(min_length=1)
    short_summary: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    tags: List[str]
    importance_score: float = Field(ge=0, le=10)
    is_israeli_relevant: bool

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, tags: List[str]) -> List[str]:
        cleaned = [tag.strip() for tag in tags if tag.strip()]
        return cleaned[:MAX_TAGS]
