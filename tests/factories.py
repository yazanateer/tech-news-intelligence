from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import Article, ArticleEnrichment, Source


def make_article(db: Session, source: Source, **overrides: Any) -> Article:
    index = db.query(Article).count() + 1
    data: Dict[str, Any] = {
        "source_id": source.id,
        "title": f"Article {index}",
        "url": f"https://example.com/{index}",
        "canonical_url": f"https://example.com/{index}",
        "title_hash": f"hash-{index}",
        "published_at": datetime.now(timezone.utc),
    }
    data.update(overrides)
    article = Article(**data)
    db.add(article)
    db.commit()
    return article


def make_enrichment(
    db: Session,
    article: Article,
    importance_score: Optional[float] = 5.0,
    is_israeli_relevant: bool = True,
) -> ArticleEnrichment:
    enrichment = ArticleEnrichment(
        article_id=article.id,
        model_name="test-model",
        short_summary="summary",
        why_it_matters="why",
        tags=["tag"],
        importance_score=importance_score,
        is_israeli_relevant=is_israeli_relevant,
    )
    db.add(enrichment)
    db.commit()
    return enrichment


VALID_AI_RESULT: Dict[str, Any] = {
    "category": "סייבר",
    "short_summary": "סיכום קצר",
    "why_it_matters": "למה זה חשוב",
    "tags": ["סייבר", "השקעות"],
    "importance_score": 8,
    "is_israeli_relevant": True,
}


class FakeAIClient:
    """Stands in for OpenAIClient; returns a canned result or raises."""

    model = "fake-model"

    def __init__(self, result: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self.result = result if result is not None else dict(VALID_AI_RESULT)
        self.error = error
        self.calls = 0

    def generate_json(self, **kwargs: Any) -> Dict[str, Any]:
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


class FakeFetcher:
    def __init__(self, content: str = "", error: Exception = None) -> None:
        self.content = content
        self.error = error

    def fetch(self, feed_url: str) -> str:
        if self.error:
            raise self.error
        return self.content
