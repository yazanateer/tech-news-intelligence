from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.article import Article
from app.repositories.enrichment_repository import EnrichmentRepository
from app.services.ai.openai_client import OpenAIClient


class EnrichmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.openai_client = OpenAIClient()
        self.enrichment_repository = EnrichmentRepository(db)

    def enrich_article(self, article: Article) -> Dict[str, Any]:
        existing_enrichment = self.enrichment_repository.get_by_article_id(article.id)
        if existing_enrichment:
            raise ValueError(f"Article {article.id} is already enriched")

        article_payload = {
            "title": article.title,
            "cleaned_content": article.cleaned_content,
            "source_id": article.source_id,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "language": article.language,
        }

        ai_result = self.openai_client.enrich_article(article_payload)

        enrichment_data = {
            "article_id": article.id,
            "model_name": self.openai_client.model,
            "category": ai_result.get("category"),
            "short_summary": ai_result.get("short_summary"),
            "why_it_matters": ai_result.get("why_it_matters"),
            "key_entities": None,
            "tags": ai_result.get("tags"),
            "importance_score": ai_result.get("importance_score"),
            "confidence_score": None,
            "is_israeli_relevant": ai_result.get("is_israeli_relevant", False),
            "raw_llm_response": ai_result,
        }

        self.enrichment_repository.create(enrichment_data)
        self.db.commit()

        return ai_result