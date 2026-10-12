import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class FeedFetchError(Exception):
    """Raised when an RSS feed cannot be downloaded."""


class RSSFetcher:
    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds or settings.rss_timeout_seconds
        self.transport = transport

    def fetch(self, feed_url: str) -> str:
        # Errors are raised (not logged) so the caller logs each failure once.
        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                transport=self.transport,
            ) as client:
                response = client.get(feed_url)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise FeedFetchError(
                f"HTTP {exc.response.status_code} from {feed_url}"
            ) from exc
        except httpx.RequestError as exc:
            raise FeedFetchError(
                f"Request to {feed_url} failed: {exc.__class__.__name__}"
            ) from exc

        logger.info("Fetched RSS feed successfully: %s", feed_url)
        return response.text
