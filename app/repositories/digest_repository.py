from typing import List

from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment


class DigestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_top_enriched_articles(self, limit: int = 5) -> List[tuple]:
        return (
            self.db.query(Article, ArticleEnrichment)
            .join(
                ArticleEnrichment,
                ArticleEnrichment.article_id == Article.id,
            )
            .order_by(
                ArticleEnrichment.importance_score.desc(),
                Article.published_at.desc(),
            )
            .limit(limit)
            .all()
        )