import pytest
from pydantic import ValidationError

from app.schemas.enrichment import EnrichmentResult
from tests.factories import VALID_AI_RESULT


def test_valid_result_is_accepted() -> None:
    result = EnrichmentResult.model_validate(VALID_AI_RESULT)

    assert result.importance_score == 8


def test_tags_are_trimmed_and_limited_to_three() -> None:
    data = dict(VALID_AI_RESULT, tags=["a", " ", "b ", "c", "d"])

    assert EnrichmentResult.model_validate(data).tags == ["a", "b", "c"]


@pytest.mark.parametrize("score", [-1, 11])
def test_out_of_range_importance_is_rejected(score: float) -> None:
    with pytest.raises(ValidationError):
        EnrichmentResult.model_validate(dict(VALID_AI_RESULT, importance_score=score))


def test_missing_field_is_rejected() -> None:
    data = dict(VALID_AI_RESULT)
    del data["short_summary"]

    with pytest.raises(ValidationError):
        EnrichmentResult.model_validate(data)
