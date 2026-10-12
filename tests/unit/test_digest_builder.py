from types import SimpleNamespace

from app.services.ranking.digest_builder import DigestBuilder


def _item(title: str, score: float = 8.0, tags=None):
    article = SimpleNamespace(title=title, canonical_url=f"https://example.com/{title}")
    enrichment = SimpleNamespace(
        short_summary="סיכום",
        why_it_matters="חשוב",
        tags=tags if tags is not None else ["AI", "סייבר"],
        importance_score=score,
    )
    return article, enrichment


def test_build_messages_creates_one_message_per_article() -> None:
    messages = DigestBuilder().build_messages([_item("a"), _item("b")])

    assert len(messages) == 2
    assert "(1/2)" in messages[0]
    assert "(2/2)" in messages[1]
    assert "https://example.com/b" in messages[1]


def test_format_includes_score_and_tags() -> None:
    message = DigestBuilder().build_messages([_item("a", score=7.5)])[0]

    assert "7.5/10" in message
    assert "AI, סייבר" in message


def test_missing_values_use_placeholder() -> None:
    article, enrichment = _item("a", tags=[])
    enrichment.importance_score = None

    message = DigestBuilder().build_messages([(article, enrichment)])[0]

    assert "לא זמין" in message


def test_empty_digest() -> None:
    builder = DigestBuilder()

    assert builder.build_messages([]) == ["עדכון חדשות טכנולוגיה\n\nלא נמצאו כתבות מועשרות."]
    assert "לא נמצאו כתבות מועשרות." in builder.build([])


def test_build_contains_all_articles() -> None:
    digest = DigestBuilder().build([_item("first"), _item("second")])

    assert "1. first" in digest
    assert "2. second" in digest
