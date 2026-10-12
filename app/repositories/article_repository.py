from typing import List, Optional

from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment

STATUS_ENRICHED = "enriched"
STATUS_ENRICHMENT_FAILED = "enrichment_failed"


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_canonical_url(self, canonical_url: str) -> Optional[Article]:
        return (
            self.db.query(Article)
            .filter(Article.canonical_url == canonical_url)
            .first()
        )

    def create(self, article_data: dict) -> Article:
        article = Article(**article_data)
        self.db.add(article)
        self.db.flush()
        return article

    def get_pending_enrichment(self, limit: int) -> List[Article]:
        has_enrichment = exists().where(ArticleEnrichment.article_id == Article.id)

        return (
            self.db.query(Article)
            .filter(~has_enrichment, Article.status != STATUS_ENRICHMENT_FAILED)
            .order_by(Article.published_at.desc().nulls_last(), Article.id.desc())
            .limit(limit)
            .all()
        )

    def update_status(self, article: Article, status: str) -> None:
        article.status = status
        self.db.flush()
