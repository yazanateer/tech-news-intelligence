from datetime import datetime, timedelta, timezone

from app.repositories.article_repository import STATUS_ENRICHMENT_FAILED, ArticleRepository
from app.repositories.digest_repository import DigestRepository
from tests.factories import make_article, make_enrichment

NOW = datetime.now(timezone.utc)


def test_pending_enrichment_excludes_enriched_and_failed(db, source) -> None:
    pending = make_article(db, source)
    enriched = make_article(db, source)
    make_enrichment(db, enriched)
    make_article(db, source, status=STATUS_ENRICHMENT_FAILED)

    result = ArticleRepository(db).get_pending_enrichment(limit=10)

    assert [article.id for article in result] == [pending.id]


def test_pending_enrichment_orders_newest_first_and_respects_limit(db, source) -> None:
    make_article(db, source, published_at=NOW - timedelta(days=2))
    newest = make_article(db, source, published_at=NOW)
    make_article(db, source, published_at=None)

    result = ArticleRepository(db).get_pending_enrichment(limit=1)

    assert [article.id for article in result] == [newest.id]


def test_digest_ranks_by_importance_within_window(db, source) -> None:
    low = make_article(db, source)
    high = make_article(db, source)
    old = make_article(db, source, published_at=NOW - timedelta(days=3))
    make_enrichment(db, low, importance_score=3)
    make_enrichment(db, high, importance_score=9)
    make_enrichment(db, old, importance_score=10)

    items = DigestRepository(db).get_top_enriched_articles(
        limit=5, since=NOW - timedelta(hours=24)
    )

    assert [article.id for article, _ in items] == [high.id, low.id]


def test_digest_filters_non_israeli_articles(db, source) -> None:
    israeli = make_article(db, source)
    foreign = make_article(db, source)
    make_enrichment(db, israeli, is_israeli_relevant=True)
    make_enrichment(db, foreign, is_israeli_relevant=False, importance_score=10)
    since = NOW - timedelta(hours=24)
    repository = DigestRepository(db)

    israeli_only = repository.get_top_enriched_articles(limit=5, since=since)
    everything = repository.get_top_enriched_articles(limit=5, since=since, israeli_only=False)

    assert [article.id for article, _ in israeli_only] == [israeli.id]
    assert len(everything) == 2
