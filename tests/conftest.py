from pathlib import Path
from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Source
from app.models.base import Base

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_feed() -> str:
    return (FIXTURES_DIR / "sample_feed.xml").read_text(encoding="utf-8")


@pytest.fixture
def db() -> Iterator[Session]:
    """In-memory SQLite session so DB tests run without Postgres."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def source(db: Session) -> Source:
    source = Source(
        name="Sample",
        slug="sample",
        feed_url="https://example.com/feed.xml",
        language="he",
        country="IL",
        category="tech",
        priority_weight=1.0,
    )
    db.add(source)
    db.commit()
    return source
