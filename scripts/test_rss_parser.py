import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.repositories.source_repository import SourceRepository
from app.services.ingestion.rss_fetcher import RSSFetcher
from app.services.ingestion.rss_parser import RSSParser

def main() -> None:
    db = SessionLocal()

    try:
        source_repository = SourceRepository(db)
        rss_fetcher = RSSFetcher()
        rss_parser = RSSParser()

        sources = source_repository.get_active_rss_sources()
        print(f"Found {len(sources)} active RSS sources.")
        for source in sources:
            print(f"\nFetching and parsing source: {source.name} ({source.feed_url}")

            try:
                rss_content = rss_fetcher.fetch(source.feed_url)
                parsed_entries = rss_parser.parse(rss_content)

                print(f"Parsed {len(parsed_entries)} entries from {source.slug}")

                if parsed_entries:
                    print("\nFirst parsed entry:")
                    print(parsed_entries[0])
                print("-" * 80)
            except Exception as e:
                print(f"Failed for {source.slug}: {e}")
                continue
    finally:
        db.close()


if __name__ == "__main__":
    main()