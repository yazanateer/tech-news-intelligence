from typing import Optional

from sqlalchemy.orm import Session

from app.models.article import Article

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
