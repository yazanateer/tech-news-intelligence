import logging

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.repositories.source_repository import SourceRepository

logger = logging.getLogger(__name__)


SOURCES = [
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
        "is_active": True,
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
        "is_active": True,
        "poll_interval_minutes": 10,
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
]


def seed_sources() -> None:
    setup_logging()

    db = SessionLocal()
    try:
        repository = SourceRepository(db)

        for source_data in SOURCES:
            if repository.get_by_slug(source_data["slug"]):
                logger.info("Skipping existing source: %s", source_data["slug"])
                continue

            repository.create(source_data)
            logger.info("Added source: %s", source_data["slug"])

        db.commit()
        logger.info("Source seeding completed successfully.")
    except Exception:
        db.rollback()
        logger.exception("Source seeding failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sources()
