# app/api/dependencies.py
from fastapi import Depends
from app.services.llm import LLMService
from app.services.storage import StorageService
from app.config import get_settings
from typing import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_llm_service(
    settings = Depends(get_settings)
) -> AsyncGenerator[LLMService, None]:
    service = LLMService(settings.GROQ_API_KEY)
    try:
        yield service
    finally:
        # No need for cleanup for LLM service
        pass

@asynccontextmanager
async def get_storage_service(
    settings = Depends(get_settings)
) -> AsyncGenerator[StorageService, None]:
    service = StorageService()
    try:
        yield service
    finally:
        await service.cleanup()