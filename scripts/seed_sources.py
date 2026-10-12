"""Sync the RSS sources below into the database.

New sources are created and existing ones (matched by slug) are updated, so
this list is the source of truth. Retired sources stay in the list with
is_active=False to keep their historical articles linked.
"""
import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.repositories.source_repository import SourceRepository
from scripts.common import run_cli

logger = logging.getLogger(__name__)


SOURCES: List[Dict[str, Any]] = [
    {
        "name": "Globes Technology",
        "slug": "globes-tech",
        "source_type": "rss",
        "feed_url": "https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=594",
        "site_url": "https://www.globes.co.il",
        "language": "he",
        "country": "IL",
        "category": "tech",
        "priority_weight": 1.20,
        "is_active": True,
        "poll_interval_minutes": 10,
    },
    {
        "name": "Techtime News",
        "slug": "techtime",
        "source_type": "rss",
        "feed_url": "https://techtime.news/feed/",
        "site_url": "https://techtime.news",
        "language": "en",
        "country": "IL",
        "category": "tech",
        "priority_weight": 1.10,
        "is_active": True,
        "poll_interval_minutes": 30,
    },
    {
        "name": "Geektime",
        "slug": "geektime",
        "source_type": "rss",
        "feed_url": "https://www.geektime.co.il/feed/",
        "site_url": "https://www.geektime.co.il",
        "language": "he",
        "country": "IL",
        "category": "tech",
        "priority_weight": 1.00,
        "is_active": True,
        "poll_interval_minutes": 15,
    },
    # Retired 2026-10-12: these feeds return HTTP 404 and neither site
    # publishes a public RSS feed anymore.
    {
        "name": "Calcalist Tech",
        "slug": "calcalist-tech",
        "source_type": "rss",
        "feed_url": "https://www.calcalist.co.il/GeneralRSS/0,16335,L-8,00.xml",
        "site_url": "https://www.calcalist.co.il",
        "language": "he",
        "country": "IL",
        "category": "tech",
        "priority_weight": 1.20,
        "is_active": False,
        "poll_interval_minutes": 10,
    },
    {
        "name": "CTech",
        "slug": "ctech",
        "source_type": "rss",
        "feed_url": "https://www.calcalistech.com/ctechnews/rss",
        "site_url": "https://www.calcalistech.com",
        "language": "en",
        "country": "IL",
        "category": "tech",
        "priority_weight": 1.10,
        "is_active": False,
        "poll_interval_minutes": 10,
    },
]


def sync_sources(db: Session, sources: List[Dict[str, Any]]) -> None:
    repository = SourceRepository(db)

    for source_data in sources:
        existing = repository.get_by_slug(source_data["slug"])

        if existing:
            repository.update(existing, source_data)
            logger.info("Updated source: %s (active=%s)", source_data["slug"], source_data["is_active"])
        else:
            repository.create(source_data)
            logger.info("Added source: %s", source_data["slug"])

    db.commit()


def main() -> None:
    setup_logging()

    db = SessionLocal()
    try:
        sync_sources(db, SOURCES)
        logger.info("Source sync completed successfully.")
    except Exception:
        db.rollback()
        logger.exception("Source sync failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_cli(main)
