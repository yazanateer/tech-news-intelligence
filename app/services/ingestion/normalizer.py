import calendar
import html
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional

from app.models.source import Source
from app.services.processing.hasher import Hasher
from app.services.processing.url_canonicalizer import URLCanonicalizer


class RSSNormalizer:
    def __init__(self) -> None:
        self.url_canonicalizer = URLCanonicalizer()
        self.hasher = Hasher()

    def normalize(self, source: Source, entry: Dict[str, Any]) -> Dict[str, Any]:
        title = self._clean_text(entry.get("title"))
        url = self._clean_text(entry.get("link"))
        description = self._clean_html(entry.get("description"))
        published_at = self._parse_published_at(entry)
        external_id = self._clean_text(entry.get("external_id"))
        canonical_url = self.url_canonicalizer.canonicalize(url) if url else ""
        title_hash = self.hasher.sha256(title) if title else ""
        content_hash = self.hasher.sha256(description) if description else None

        return {
            "source_id": source.id,
            "external_id": external_id,
            "title": title,
            "url": url,
            "canonical_url": canonical_url,
            "author": None,
            "published_at": published_at,
            "raw_description": entry.get("description"),
            "raw_content": None,
            "cleaned_content": description,
            "language": source.language,
            "country_relevance": source.country,
            "title_hash": title_hash,
            "content_hash": content_hash,
            "status": "ingested",
            "is_duplicated": False,
            "duplicated_of_article_id": None,
        }

    def _clean_text(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    def _clean_html(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value)
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text or None

    def _parse_published_at(self, entry: Dict[str, Any]) -> Optional[datetime]:
        # feedparser already parses RSS and Atom dates into a UTC struct_time.
        parsed = entry.get("published_parsed")
        if isinstance(parsed, time.struct_time):
            return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)

        return self._parse_rfc822(entry.get("published"))

    def _parse_rfc822(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None

        try:
            return parsedate_to_datetime(str(value))
        except Exception:
            return None
