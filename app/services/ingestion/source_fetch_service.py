import logging

from sqlalchemy.orm import Session

from app.repositories.article_repository import ArticleRepository
from app.repositories.source_repository import SourceRepository
from app.services.ingestion.normalizer import RSSNormalizer
from app.services.ingestion.rss_fetcher import RSSFetcher
from app.services.ingestion.rss_parser import RSSParser

logger = logging.getLogger(__name__)


class SourceFetchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.source_repository = SourceRepository(db)
        self.article_repository = ArticleRepository(db)
        self.rss_fetcher = RSSFetcher()
        self.rss_parser = RSSParser()
        self.normalizer = RSSNormalizer()

    def ingest_active_sources(self) -> None:
        sources = self.source_repository.get_active_rss_sources()

        logger.info("Found %s active RSS sources", len(sources))

        for source in sources:
            logger.info("Processing source: %s", source.slug)

            try:
                rss_content = self.rss_fetcher.fetch(source.feed_url)
                parsed_entries = self.rss_parser.parse(rss_content)

                logger.info(
                    "Parsed %s entries from source %s",
                    len(parsed_entries),
                    source.slug,
                )

                created_count = 0
                skipped_count = 0

                for entry in parsed_entries:
                    normalized = self.normalizer.normalize(source, entry)

                    if not normalized["canonical_url"]:
                        skipped_count += 1
                        continue

                    existing_article = self.article_repository.get_by_canonical_url(
                        normalized["canonical_url"]
                    )

                    if existing_article:
                        skipped_count += 1
                        continue

                    self.article_repository.create(normalized)
                    created_count += 1
                self.db.commit()

                logger.info(
                "Source %s completed: created=%s skipped=%s",
                source.slug,
                created_count,
                skipped_count
                )

            except Exception as e:
                self.db.rollback()
                logger.exception("Failed processing source %s: %s", source.slug, e)