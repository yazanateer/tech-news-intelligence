from datetime import datetime
from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment


class DigestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_top_enriched_articles(
        self,
        limit: int,
        since: datetime,
        israeli_only: bool = True,
    ) -> List[Tuple[Article, ArticleEnrichment]]:
        article_time = func.coalesce(Article.published_at, Article.created_at)

        query = (
            self.db.query(Article, ArticleEnrichment)
            .join(ArticleEnrichment, ArticleEnrichment.article_id == Article.id)
            .filter(article_time >= since)
        )

        if israeli_only:
            query = query.filter(ArticleEnrichment.is_israeli_relevant.is_(True))

        return (
            query.order_by(
                ArticleEnrichment.importance_score.desc().nulls_last(),
                Article.published_at.desc().nulls_last(),
            )
            .limit(limit)
            .all()
        )
