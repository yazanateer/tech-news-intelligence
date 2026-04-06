import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.ingestion.source_fetch_service import SourceFetchService


def main() -> None:
    setup_logging()

    db = SessionLocal()

    try:
        service = SourceFetchService(db)
        service.ingest_active_sources()
        print("Ingestion completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()