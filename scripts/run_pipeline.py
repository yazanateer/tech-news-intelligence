"""Run the full pipeline: ingest -> enrich -> build digest -> send to WhatsApp.

Usage:
    python -m scripts.run_pipeline              # full run, sends WhatsApp
    python -m scripts.run_pipeline --no-send    # everything except delivery
"""
import argparse
import logging

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.pipeline_service import PipelineService
from scripts.common import save_digest

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the news digest pipeline.")
    parser.add_argument(
        "--no-send",
        action="store_true",
        help="Build the digest but do not send it to WhatsApp.",
    )
    parser.add_argument(
        "--enrich-limit",
        type=int,
        default=None,
        help="Max articles to enrich in this run (default: ENRICHMENT_BATCH_SIZE).",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    db = SessionLocal()
    try:
        result = PipelineService(db).run(send=not args.no_send, enrich_limit=args.enrich_limit)
        output_file = save_digest(result.digest.text)
        logger.info("Digest saved to %s", output_file)
    finally:
        db.close()


if __name__ == "__main__":
    main()
