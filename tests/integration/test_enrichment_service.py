import pytest

from app.models import Article, ArticleEnrichment
from app.repositories.article_repository import STATUS_ENRICHED, STATUS_ENRICHMENT_FAILED
from app.services.ai.enrichment_service import ArticleAlreadyEnrichedError, EnrichmentService
from app.services.ai.openai_client import AIClientError
from tests.factories import VALID_AI_RESULT, FakeAIClient, make_article, make_enrichment


def test_enrich_article_saves_validated_result(db, source) -> None:
    article = make_article(db, source)

    enrichment = EnrichmentService(db, openai_client=FakeAIClient()).enrich_article(article)

    assert enrichment.model_name == "fake-model"
    assert enrichment.importance_score == 8
    assert enrichment.raw_llm_response == VALID_AI_RESULT
    assert db.get(Article, article.id).status == STATUS_ENRICHED


def test_enrich_article_rejects_already_enriched(db, source) -> None:
    article = make_article(db, source)
    make_enrichment(db, article)

    with pytest.raises(ArticleAlreadyEnrichedError):
        EnrichmentService(db, openai_client=FakeAIClient()).enrich_article(article)


def test_enrich_pending_enriches_all_pending_articles(db, source) -> None:
    make_article(db, source)
    make_article(db, source)
    ai_client = FakeAIClient()

    result = EnrichmentService(db, openai_client=ai_client).enrich_pending(limit=10)

    assert (result.enriched, result.failed) == (2, 0)
    assert db.query(ArticleEnrichment).count() == 2


def test_enrich_pending_is_idempotent(db, source) -> None:
    make_article(db, source)
    ai_client = FakeAIClient()
    service = EnrichmentService(db, openai_client=ai_client)

    service.enrich_pending(limit=10)
    second_run = service.enrich_pending(limit=10)

    assert second_run.enriched == 0
    assert ai_client.calls == 1


def test_enrich_pending_marks_api_failures(db, source) -> None:
    article = make_article(db, source)
    ai_client = FakeAIClient(error=AIClientError("down"))

    result = EnrichmentService(db, openai_client=ai_client).enrich_pending(limit=10)

    assert (result.enriched, result.failed) == (0, 1)
    assert db.get(Article, article.id).status == STATUS_ENRICHMENT_FAILED
    assert db.query(ArticleEnrichment).count() == 0


def test_enrich_pending_marks_invalid_llm_output(db, source) -> None:
    article = make_article(db, source)
    ai_client = FakeAIClient(result=dict(VALID_AI_RESULT, importance_score=42))

    result = EnrichmentService(db, openai_client=ai_client).enrich_pending(limit=10)

    assert result.failed == 1
    assert db.get(Article, article.id).status == STATUS_ENRICHMENT_FAILED
