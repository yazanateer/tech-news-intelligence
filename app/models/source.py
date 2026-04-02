from typing import Optional

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="rss")
    feed_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    site_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="he")
    country: Mapped[str] = mapped_column(String(10), nullable=False, default="IL")
    priority_weight: Mapped[float] = mapped_column(Numeric(3,2), nullable=False, default=1.00)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    poll_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )