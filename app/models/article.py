from typing import Optional

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    canonical_url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    raw_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cleaned_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="he")
    country_relevance: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    title_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ingested", index=True)
    is_duplicated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    duplicated_of_article_id: Mapped[Optional[int]] = mapped_column(ForeignKey("articles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
