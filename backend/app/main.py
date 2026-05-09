from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.logging import configure_logging

configure_logging()
app = FastAPI(title="monorepo-backend")
app.include_router(v1_router)
