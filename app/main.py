from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.contracts import router as contracts_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="API for analyzing contract compliance across multiple regulations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts_router, prefix="/api/v1")