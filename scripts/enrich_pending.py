import argparse

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.ai.enrichment_service import EnrichmentService


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="Enrich pending articles with OpenAI.")
    parser.add_argument("--limit", type=int, default=settings.enrichment_batch_size)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        EnrichmentService(db).enrich_pending(args.limit)
    finally:
        db.close()


if __name__ == "__main__":
    main()
