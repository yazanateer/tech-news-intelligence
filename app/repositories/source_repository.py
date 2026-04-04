from typing import Type

from sqlalchemy.orm import Session

from app.models.source import Source


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_rss_sources(self) -> list[Type[Source]]:
        return (
            self.db.query(Source)
            .filter(Source.is_active.is_(True), Source.source_type == "rss")
            .order_by(Source.priority_weight.desc(), Source.id.asc())
            .all()
        )