import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.repositories.source_repository import SourceRepository
from app.services.ingestion.normalizer import RSSNormalizer
from app.services.ingestion.rss_fetcher import RSSFetcher
from app.services.ingestion.rss_parser import RSSParser

def main() -> None:
    db = SessionLocal()

    try:
        source_repository = SourceRepository(db)
        rss_fetcher = RSSFetcher()
        rss_parser = RSSParser()
        normalizer = RSSNormalizer()

        sources = source_repository.get_active_rss_sources()

        for source in sources:
            print(f"\nNormalizing source: {source.name}")

            rss_content = rss_fetcher.fetch(source.feed_url)
            parsed_entries = rss_parser.parse(rss_content)

            if not parsed_entries:
                print("No entries found.")
                continue

            normalized = normalizer.normalize(source, parsed_entries[0])

            print("Normalized entry:")
            for key, value in normalized.items():
                print(f"{key}: {value}")
            print("-" * 80)
    finally:
        db.close()


if __name__ == "__main__":
    main()