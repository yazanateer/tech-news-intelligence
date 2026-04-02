from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.redis import redis_client

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    db_ok = False
    redis_ok = False

    try:
        db = SessionLocal()
        db.execute(text["Select 1"])
        db_ok = True
    except Exception:
        db_ok = False
    finally:
        try:
            db.close()
        except Exception:
            pass

    try:
        redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    status = "ok" if db_ok and redis_ok else "degraded"

    return {
        "status": status,
        "databases": db_ok,
        "redis": redis_ok
    }