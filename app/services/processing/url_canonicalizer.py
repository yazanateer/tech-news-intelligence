from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


class URLCanonicalizer:
    TRACKING_PARAMS = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid"
    }

    def canonicalize(self, url: str) -> str:
        parsed = urlparse(url)

        clean_query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key not in self.TRACKING_PARAMS
        ]

        normalized = parsed._replace(
            query=urlencode(clean_query),
            fragment="",
        )

        return urlunparse(normalized)
