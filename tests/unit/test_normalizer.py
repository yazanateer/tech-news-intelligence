import time
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.ingestion.normalizer import RSSNormalizer

SOURCE = SimpleNamespace(id=1, language="he", country="IL")


def test_normalize_cleans_html_and_canonicalizes_url() -> None:
    entry = {
        "title": "  Title  ",
        "link": "https://example.com/a?utm_source=rss#top",
        "description": "<p>Hello &amp; <b>world</b></p>",
    }

    normalized = RSSNormalizer().normalize(SOURCE, entry)

    assert normalized["title"] == "Title"
    assert normalized["canonical_url"] == "https://example.com/a"
    assert normalized["cleaned_content"] == "Hello & world"
    assert normalized["source_id"] == 1
    assert len(normalized["title_hash"]) == 64


def test_normalize_prefers_published_parsed() -> None:
    entry = {
        "title": "t",
        "link": "https://example.com",
        "published": "not a date",
        "published_parsed": time.strptime("2026-04-06 07:00:00", "%Y-%m-%d %H:%M:%S"),
    }

    normalized = RSSNormalizer().normalize(SOURCE, entry)

    assert normalized["published_at"] == datetime(2026, 4, 6, 7, 0, tzinfo=timezone.utc)


def test_normalize_falls_back_to_rfc822_date() -> None:
    entry = {"title": "t", "link": "https://example.com", "published": "Mon, 06 Apr 2026 10:00:00 +0300"}

    published_at = RSSNormalizer().normalize(SOURCE, entry)["published_at"]

    assert published_at == datetime(2026, 4, 6, 7, 0, tzinfo=timezone.utc)


def test_normalize_invalid_date_returns_none() -> None:
    entry = {"title": "t", "link": "https://example.com", "published": "yesterday"}

    assert RSSNormalizer().normalize(SOURCE, entry)["published_at"] is None


def test_normalize_missing_title_and_link() -> None:
    normalized = RSSNormalizer().normalize(SOURCE, {})

    assert normalized["title"] is None
    assert normalized["canonical_url"] == ""
    assert normalized["title_hash"] == ""
