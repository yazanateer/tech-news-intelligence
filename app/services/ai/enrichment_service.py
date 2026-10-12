import logging
from dataclasses import dataclass
from typing import Optional

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment
from app.repositories.article_repository import (
    STATUS_ENRICHED,
    STATUS_ENRICHMENT_FAILED,
    ArticleRepository,
)
from app.repositories.enrichment_repository import EnrichmentRepository
from app.schemas.enrichment import EnrichmentResult
from app.services.ai.openai_client import AIClientError, OpenAIClient
from app.services.ai.prompts import (
    ENRICHMENT_JSON_SCHEMA,
    ENRICHMENT_SCHEMA_NAME,
    SYSTEM_PROMPT,
    build_article_enrichment_prompt,
)

logger = logging.getLogger(__name__)


class ArticleAlreadyEnrichedError(Exception):
    """Raised when trying to enrich an article that already has an enrichment."""


@dataclass
class EnrichmentBatchResult:
    enriched: int = 0
    failed: int = 0


class EnrichmentService:
    def __init__(self, db: Session, openai_client: Optional[OpenAIClient] = None) -> None:
        self.db = db
        self.openai_client = openai_client or OpenAIClient()
        self.article_repository = ArticleRepository(db)
        self.enrichment_repository = EnrichmentRepository(db)

    def enrich_pending(self, limit: int) -> EnrichmentBatchResult:
        articles = self.article_repository.get_pending_enrichment(limit)
        logger.info("Found %s articles pending enrichment", len(articles))

        result = EnrichmentBatchResult()
        total = len(articles)

        for position, article in enumerate(articles, start=1):
            logger.info(
                "Enriching article %s/%s (id=%s): %s",
                position,
                total,
                article.id,
                article.title,
            )
            try:
                self.enrich_article(article)
                result.enriched += 1
            except (AIClientError, ValidationError) as exc:
                self.db.rollback()
                self._mark_failed(article)
                result.failed += 1
                logger.error("Enrichment failed for article %s: %s", article.id, exc)

        logger.info(
            "Enrichment finished: enriched=%s failed=%s",
            result.enriched,
            result.failed,
        )
        return result

    def enrich_article(self, article: Article) -> ArticleEnrichment:
        if self.enrichment_repository.get_by_article_id(article.id):
            raise ArticleAlreadyEnrichedError(f"Article {article.id} is already enriched")

        raw_result = self.openai_client.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_article_enrichment_prompt(self._build_payload(article)),
            schema_name=ENRICHMENT_SCHEMA_NAME,
            schema=ENRICHMENT_JSON_SCHEMA,
        )
        result = EnrichmentResult.model_validate(raw_result)

        enrichment = self.enrichment_repository.create(
            {
                "article_id": article.id,
                "model_name": self.openai_client.model,
                "category": result.category,
                "short_summary": result.short_summary,
                "why_it_matters": result.why_it_matters,
                "key_entities": None,
                "tags": result.tags,
                "importance_score": result.importance_score,
                "confidence_score": None,
                "is_israeli_relevant": result.is_israeli_relevant,
                "raw_llm_response": raw_result,
            }
        )
        self.article_repository.update_status(article, STATUS_ENRICHED)
        self.db.commit()

        return enrichment

    def _build_payload(self, article: Article) -> dict:
        return {
            "title": article.title,
            "cleaned_content": article.cleaned_content,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "language": article.language,
        }

    def _mark_failed(self, article: Article) -> None:
        self.article_repository.update_status(article, STATUS_ENRICHMENT_FAILED)
        self.db.commit()
