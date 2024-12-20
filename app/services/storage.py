from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.config import get_settings
from app.utils import StorageError, logger
import tempfile
import uuid
import shutil
import os

class StorageService:
    def __init__(self):
        self.settings = get_settings()
        self.temp_dir = Path(tempfile.gettempdir()) / "contract_analyzer"
        self._ensure_temp_dir()

    def _ensure_temp_dir(self):
        """Ensure temporary directory exists."""
        try:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create temp directory: {str(e)}")
            raise StorageError(f"Storage initialization failed: {str(e)}")

    async def save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary storage."""
        try:
            # Generate unique filename
            ext = Path(file.filename).suffix
            temp_filename = f"{uuid.uuid4()}{ext}"
            temp_path = self.temp_dir / temp_filename

            # Save file
            content = await file.read()
            with open(temp_path, 'wb') as f:
                f.write(content)

            return str(temp_path)
        except Exception as e:
            logger.error(f"Failed to save temp file: {str(e)}")
            raise StorageError(f"File save failed: {str(e)}")

    async def delete_temp_file(self, file_path: str):
        """Delete temporary file."""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
        except Exception as e:
            logger.error(f"Failed to delete temp file: {str(e)}")
            raise StorageError(f"File deletion failed: {str(e)}")

    async def cleanup(self):
        """Cleanup temporary files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {str(e)}")
            raise StorageError(f"Cleanup failed: {str(e)}")