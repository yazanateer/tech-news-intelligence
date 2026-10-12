import logging

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.pipeline_service import PipelineService
from scripts.common import save_digest

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()

    db = SessionLocal()
    try:
        digest = PipelineService(db).build_digest()
        logger.info("Digest preview:\n%s", digest.text)
        logger.info("Digest saved to %s", save_digest(digest.text))
    finally:
        db.close()


if __name__ == "__main__":
    main()
