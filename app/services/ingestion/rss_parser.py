from typing import Any, Dict, List

import feedparser


class RSSParser:
    def parse(self, rss_content: str) -> List[Dict[str, Any]]:
        parsed_feed = feedparser.parse(rss_content)

        entries: List[Dict[str, Any]] = []

        for entry in parsed_feed.entries:
            entries.append(
                {
                    "title": getattr(entry, "title", None),
                    "link": getattr(entry, "link", None),
                    "description": getattr(entry, "summary", None),
                    "published": getattr(entry, "published", None),
                    "external_id": getattr(entry, "id", None),
                }
            )

            return entries