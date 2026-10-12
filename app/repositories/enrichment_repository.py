from typing import Optional

from sqlalchemy.orm import Session

from app.models.article_enrichment import ArticleEnrichment


class EnrichmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_article_id(self, article_id: int) -> Optional[ArticleEnrichment]:
        return (
            self.db.query(ArticleEnrichment)
            .filter(ArticleEnrichment.article_id == article_id)
            .first()
        )

    def create(self, enrichment_data: dict) -> ArticleEnrichment:
        enrichment = ArticleEnrichment(**enrichment_data)
        self.db.add(enrichment)
        self.db.flush()
        return enrichment
