import logging
from typing import Dict

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> Dict[str, object]:
    db_ok = _check_database()

    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
    }


def _check_database() -> bool:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        return False
    finally:
        db.close()
