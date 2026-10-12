from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.ingestion.source_fetch_service import SourceFetchService


def main() -> None:
    setup_logging()

    db = SessionLocal()
    try:
        SourceFetchService(db).ingest_active_sources()
    finally:
        db.close()


if __name__ == "__main__":
    main()
