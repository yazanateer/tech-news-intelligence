import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.repositories.source_repository import SourceRepository
from app.services.ingestion.rss_fetcher import RSSFetcher

def main() -> None:
    db = SessionLocal()

    try:
        source_repository = SourceRepository(db)
        rss_fetcher = RSSFetcher(500)

        sources = source_repository.get_active_rss_sources()
        print(f"Found {len(sources)} active RSS sources.")

        for source in sources:
            print(f"\nFetching source: {source.name} ({source.feed_url}")
            rss_content = rss_fetcher.fetch(source.feed_url)

            print(f"Fetched {len(rss_content)} characters from {source.slug}")
            print(rss_content[:300])
            print("-" * 80)
    finally:
        db.close()


if __name__ == "__main__":
    main()