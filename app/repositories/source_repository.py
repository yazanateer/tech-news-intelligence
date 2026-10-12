from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.source import Source


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_rss_sources(self) -> List[Source]:
        return (
            self.db.query(Source)
            .filter(Source.is_active.is_(True), Source.source_type == "rss")
            .order_by(Source.priority_weight.desc(), Source.id.asc())
            .all()
        )

    def get_by_slug(self, slug: str) -> Optional[Source]:
        return self.db.query(Source).filter(Source.slug == slug).first()

    def create(self, source_data: dict) -> Source:
        source = Source(**source_data)
        self.db.add(source)
        self.db.flush()
        return source

    def mark_fetched(self, source: Source, fetched_at: datetime) -> None:
        source.last_fetched_at = fetched_at
        self.db.flush()
