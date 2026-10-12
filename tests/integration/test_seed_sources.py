from app.models import Source
from app.repositories.source_repository import SourceRepository
from scripts.seed_sources import SOURCES, sync_sources


def test_sync_creates_all_sources(db) -> None:
    sync_sources(db, SOURCES)

    assert db.query(Source).count() == len(SOURCES)


def test_sync_updates_existing_source_and_is_idempotent(db, source) -> None:
    updated = dict(
        SOURCES[0],
        slug=source.slug,
        feed_url="https://example.com/new-feed.xml",
        is_active=False,
    )

    sync_sources(db, [updated])
    sync_sources(db, [updated])

    refreshed = db.get(Source, source.id)
    assert refreshed.feed_url == "https://example.com/new-feed.xml"
    assert refreshed.is_active is False
    assert db.query(Source).count() == 1


def test_only_active_sources_are_ingested(db) -> None:
    sync_sources(db, SOURCES)

    active_slugs = {s.slug for s in SourceRepository(db).get_active_rss_sources()}

    assert active_slugs == {"globes-tech", "techtime", "geektime"}
