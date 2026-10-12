from app.services.processing.hasher import Hasher
from app.services.processing.url_canonicalizer import URLCanonicalizer


def test_canonicalize_removes_tracking_params_and_fragment() -> None:
    url = "https://example.com/a?utm_source=rss&id=7&fbclid=abc#comments"

    assert URLCanonicalizer().canonicalize(url) == "https://example.com/a?id=7"


def test_canonicalize_keeps_url_without_query_unchanged() -> None:
    url = "https://example.com/story"

    assert URLCanonicalizer().canonicalize(url) == url


def test_urls_differing_only_in_tracking_params_are_equal() -> None:
    canonicalizer = URLCanonicalizer()

    assert canonicalizer.canonicalize(
        "https://example.com/a?id=7&utm_campaign=x"
    ) == canonicalizer.canonicalize("https://example.com/a?utm_source=y&id=7")


def test_sha256_is_deterministic_hex_digest() -> None:
    hasher = Hasher()

    assert hasher.sha256("כותרת") == hasher.sha256("כותרת")
    assert len(hasher.sha256("title")) == 64
