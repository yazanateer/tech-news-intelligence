import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.source import Source


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
    db = SessionLocal()

    try:
        for source_data in SOURCES:
            existing_source = (
                db.query(Source)
                .filter(Source.slug == source_data["slug"])
                .first()
            )

            if existing_source:
                print(f"Skipping existing source: {source_data['slug']}")
                continue

            source = Source(**source_data)
            db.add(source)
            print(f"Added source: {source_data['slug']}")

        db.commit()
        print("Source seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_sources()