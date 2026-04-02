from typing import Optional

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ArticleEnrichment(Base):
    __tablename__ = "article_enrichments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    short_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    why_it_matters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    key_entities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    importance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_israeli_relevant: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    raw_llm_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )