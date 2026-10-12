from app.models import Article, Source
from app.services.ingestion.rss_fetcher import FeedFetchError
from app.services.ingestion.source_fetch_service import SourceFetchService
from tests.factories import FakeFetcher


def test_ingest_saves_new_articles_and_skips_invalid_and_duplicates(db, source, sample_feed) -> None:
    result = SourceFetchService(db, rss_fetcher=FakeFetcher(sample_feed)).ingest_active_sources()

    titles = {article.title for article in db.query(Article).all()}
    assert result.created == 2
    assert result.skipped == 2  # entry without title + tracking-param duplicate
    assert titles == {"Israeli startup raises $24M seed", "Cyber company acquired"}
    assert db.get(Source, source.id).last_fetched_at is not None


def test_ingest_twice_does_not_duplicate_articles(db, source, sample_feed) -> None:
    service = SourceFetchService(db, rss_fetcher=FakeFetcher(sample_feed))

    service.ingest_active_sources()
    second_run = service.ingest_active_sources()

    assert second_run.created == 0
    assert db.query(Article).count() == 2


def test_failed_source_is_reported_and_does_not_raise(db, source) -> None:
    fetcher = FakeFetcher(error=FeedFetchError("HTTP 404 from https://example.com/feed.xml"))

    result = SourceFetchService(db, rss_fetcher=fetcher).ingest_active_sources()

    assert result.failed_sources == ["sample"]
    assert db.query(Article).count() == 0
