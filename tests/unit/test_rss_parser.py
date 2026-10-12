from app.services.ingestion.rss_parser import RSSParser


def test_parse_returns_every_entry(sample_feed: str) -> None:
    entries = RSSParser().parse(sample_feed)

    assert len(entries) == 4


def test_parse_maps_entry_fields(sample_feed: str) -> None:
    entry = RSSParser().parse(sample_feed)[0]

    assert entry["title"] == "Israeli startup raises $24M seed"
    assert entry["link"].startswith("https://example.com/startup-raises")
    assert entry["external_id"] == "startup-1"
    assert entry["published_parsed"] is not None


def test_parse_handles_missing_fields(sample_feed: str) -> None:
    entry = RSSParser().parse(sample_feed)[1]

    assert entry["title"] is None
    assert entry["published"] is None


def test_parse_empty_content_returns_no_entries() -> None:
    assert RSSParser().parse("") == []
