import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class RSSFetcher:
    def __init__(self, timeout_seconds: Optional[float] = None) -> None:
        self.timeout_seconds = timeout_seconds or settings.rss_timeout_seconds

    def fetch(self, feed_url: str) -> str:
        try:
            with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
                response = client.get(feed_url)
                response.raise_for_status()

            logger.info("Fetched RSS feed successfully: %s", feed_url)
            return response.text
        except httpx.HTTPStatusError as exc:
            logger.error(
                "RSS fetch failed with status error for %s: %s",
                feed_url,
                exc
            )
            raise

        except httpx.RequestError as exc:
            logger.error(
                "RSS fetch failed with request error for %s: %s",
                feed_url,
                exc
            )
            raise
