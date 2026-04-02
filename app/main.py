from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

@app.get("/")
async def root():
    return {"message": f"{settings.app_name} is running"}

app.include_router(api_router, prefix=settings.api_v1_prefix)