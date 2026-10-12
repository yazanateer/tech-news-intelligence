from app.services.ai.enrichment_service import EnrichmentService
from app.services.delivery.whatsapp_sender import DeliveryError
from app.services.ingestion.source_fetch_service import SourceFetchService
from app.services.pipeline_service import PipelineService
from tests.factories import FakeAIClient, FakeFetcher


class FakeSender:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent = []

    def send_message(self, body: str) -> str:
        if self.fail:
            raise DeliveryError("twilio down")
        self.sent.append(body)
        return "SM1"


def _pipeline(db, sample_feed: str, sender: FakeSender) -> PipelineService:
    return PipelineService(
        db,
        fetch_service=SourceFetchService(db, rss_fetcher=FakeFetcher(sample_feed)),
        enrichment_service=EnrichmentService(db, openai_client=FakeAIClient()),
        whatsapp_sender=sender,
    )


def test_run_without_send_builds_digest_but_sends_nothing(db, source, sample_feed, monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.digest_window_hours", 24 * 365 * 10)
    sender = FakeSender()

    result = _pipeline(db, sample_feed, sender).run(send=False)

    assert result.ingestion.created == 2
    assert result.enrichment.enriched == 2
    assert len(result.digest.messages) == 2
    assert result.delivery is None
    assert sender.sent == []


def test_run_with_send_delivers_each_message(db, source, sample_feed, monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.digest_window_hours", 24 * 365 * 10)
    sender = FakeSender()

    result = _pipeline(db, sample_feed, sender).run(send=True)

    assert result.delivery.sent == 2
    assert len(sender.sent) == 2


def test_delivery_failures_are_counted_not_raised(db, source, sample_feed, monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.digest_window_hours", 24 * 365 * 10)

    result = _pipeline(db, sample_feed, FakeSender(fail=True)).run(send=True)

    assert (result.delivery.sent, result.delivery.failed) == (0, 2)
