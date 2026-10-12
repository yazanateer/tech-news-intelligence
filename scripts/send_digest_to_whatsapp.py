from app.core.database import SessionLocal
from app.core.logging import setup_logging
from app.services.pipeline_service import PipelineService


def main() -> None:
    setup_logging()

    db = SessionLocal()
    try:
        service = PipelineService(db)
        service.send_messages(service.build_digest().messages)
    finally:
        db.close()


if __name__ == "__main__":
    main()
