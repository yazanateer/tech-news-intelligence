import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.digest_repository import DigestRepository
from app.services.ai.enrichment_service import EnrichmentBatchResult, EnrichmentService
from app.services.delivery.whatsapp_sender import DeliveryError, WhatsAppSender
from app.services.ingestion.source_fetch_service import IngestionResult, SourceFetchService
from app.services.ranking.digest_builder import DigestBuilder

logger = logging.getLogger(__name__)


@dataclass
class Digest:
    text: str
    messages: List[str]


@dataclass
class DeliveryResult:
    sent: int = 0
    failed: int = 0


@dataclass
class PipelineResult:
    ingestion: IngestionResult
    enrichment: EnrichmentBatchResult
    digest: Digest
    delivery: Optional[DeliveryResult] = None


class PipelineService:
    """Runs the full flow: ingest -> enrich -> build digest -> deliver."""

    def __init__(
        self,
        db: Session,
        fetch_service: Optional[SourceFetchService] = None,
        enrichment_service: Optional[EnrichmentService] = None,
        whatsapp_sender: Optional[WhatsAppSender] = None,
    ) -> None:
        self.db = db
        self.fetch_service = fetch_service
        self.enrichment_service = enrichment_service
        self.whatsapp_sender = whatsapp_sender
        self.digest_repository = DigestRepository(db)
        self.digest_builder = DigestBuilder()

    def run(self, send: bool, enrich_limit: Optional[int] = None) -> PipelineResult:
        logger.info("Pipeline started (send=%s)", send)

        fetch_service = self.fetch_service or SourceFetchService(self.db)
        enrichment_service = self.enrichment_service or EnrichmentService(self.db)

        ingestion = fetch_service.ingest_active_sources()
        enrichment = enrichment_service.enrich_pending(
            enrich_limit or settings.enrichment_batch_size
        )
        digest = self.build_digest()

        result = PipelineResult(ingestion=ingestion, enrichment=enrichment, digest=digest)

        if send:
            result.delivery = self.send_messages(digest.messages)
        else:
            logger.info("Skipping WhatsApp delivery (send disabled)")

        logger.info("Pipeline finished")
        return result

    def build_digest(self) -> Digest:
        since = datetime.now(timezone.utc) - timedelta(hours=settings.digest_window_hours)
        items = self.digest_repository.get_top_enriched_articles(
            limit=settings.digest_size,
            since=since,
            israeli_only=settings.digest_israeli_only,
        )
        logger.info("Selected %s articles for the digest", len(items))

        return Digest(
            text=self.digest_builder.build(items),
            messages=self.digest_builder.build_messages(items),
        )

    def send_messages(self, messages: List[str]) -> DeliveryResult:
        sender = self.whatsapp_sender or WhatsAppSender()
        logger.info("Sending WhatsApp digest (%s messages)...", len(messages))

        result = DeliveryResult()
        for message in messages:
            try:
                sender.send_message(message)
                result.sent += 1
            except DeliveryError:
                result.failed += 1

        logger.info("Delivery finished: sent=%s failed=%s", result.sent, result.failed)
        return result
