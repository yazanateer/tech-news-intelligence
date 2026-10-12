import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.source import Source
from app.repositories.article_repository import ArticleRepository
from app.repositories.source_repository import SourceRepository
from app.services.ingestion.normalizer import RSSNormalizer
from app.services.ingestion.rss_fetcher import RSSFetcher
from app.services.ingestion.rss_parser import RSSParser

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    created: int = 0
    skipped: int = 0
    failed_sources: List[str] = field(default_factory=list)


class SourceFetchService:
    def __init__(self, db: Session, rss_fetcher: Optional[RSSFetcher] = None) -> None:
        self.db = db
        self.source_repository = SourceRepository(db)
        self.article_repository = ArticleRepository(db)
        self.rss_fetcher = rss_fetcher or RSSFetcher()
        self.rss_parser = RSSParser()
        self.normalizer = RSSNormalizer()

    def ingest_active_sources(self) -> IngestionResult:
        sources = self.source_repository.get_active_rss_sources()
        logger.info("Found %s active RSS sources", len(sources))

        result = IngestionResult()

        for source in sources:
            try:
                created, skipped = self._ingest_source(source)
                result.created += created
                result.skipped += skipped
            except Exception as exc:
                self.db.rollback()
                result.failed_sources.append(source.slug)
                logger.error("Failed processing source %s: %s", source.slug, exc)

        logger.info(
            "Ingestion finished: created=%s skipped=%s failed_sources=%s",
            result.created,
            result.skipped,
            result.failed_sources,
        )
        return result

    def _ingest_source(self, source: Source) -> Tuple[int, int]:
        logger.info("Fetching RSS feed for source: %s", source.slug)

        rss_content = self.rss_fetcher.fetch(source.feed_url)
        entries = self.rss_parser.parse(rss_content)
        logger.info("Parsed %s entries from source %s", len(entries), source.slug)

        created = 0
        skipped = 0

        for entry in entries:
            if self._save_entry(source, entry):
                created += 1
            else:
                skipped += 1

        self.source_repository.mark_fetched(source, datetime.now(timezone.utc))
        self.db.commit()

        logger.info(
            "Source %s completed: created=%s skipped=%s",
            source.slug,
            created,
            skipped,
        )
        return created, skipped

    def _save_entry(self, source: Source, entry: Dict[str, Any]) -> bool:
        normalized = self.normalizer.normalize(source, entry)

        if not normalized["title"] or not normalized["canonical_url"]:
            logger.warning("Skipping entry without title or URL from %s", source.slug)
            return False

        if self.article_repository.get_by_canonical_url(normalized["canonical_url"]):
            return False

        # A savepoint keeps one bad entry from rolling back the whole source.
        try:
            with self.db.begin_nested():
                self.article_repository.create(normalized)
            return True
        except IntegrityError as exc:
            logger.warning(
                "Skipping entry %s from %s: %s",
                normalized["canonical_url"],
                source.slug,
                exc.orig,
            )
            return False
