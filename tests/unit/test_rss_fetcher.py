import httpx
import pytest

from app.services.ingestion.rss_fetcher import FeedFetchError, RSSFetcher

FEED_URL = "https://example.com/feed.xml"


def _fetcher(handler) -> RSSFetcher:
    return RSSFetcher(timeout_seconds=1, transport=httpx.MockTransport(handler))


def test_fetch_returns_body() -> None:
    fetcher = _fetcher(lambda request: httpx.Response(200, text="<rss/>"))

    assert fetcher.fetch(FEED_URL) == "<rss/>"


def test_http_error_raises_concise_feed_fetch_error() -> None:
    fetcher = _fetcher(lambda request: httpx.Response(404))

    with pytest.raises(FeedFetchError, match=r"^HTTP 404 from https://example.com/feed.xml$"):
        fetcher.fetch(FEED_URL)


def test_network_error_raises_feed_fetch_error() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with pytest.raises(FeedFetchError, match="ConnectError"):
        _fetcher(fail).fetch(FEED_URL)
