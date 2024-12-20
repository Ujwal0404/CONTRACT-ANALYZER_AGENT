from typing import Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def safe_json_loads(content: str) -> Dict[str, Any]:
    """Safely parse JSON content."""
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        return {}

def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Split text into chunks for LLM processing."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()

# app/utils/exceptions.py
class ContractAnalyzerError(Exception):
    """Base exception for Contract Analyzer."""
    pass

class FileParsingError(ContractAnalyzerError):
    """Raised when file parsing fails."""
    pass

class AnalysisError(ContractAnalyzerError):
    """Raised when contract analysis fails."""
    pass

class ComplianceError(ContractAnalyzerError):
    """Raised when compliance analysis fails."""
    pass

class ReportGenerationError(ContractAnalyzerError):
    """Raised when report generation fails."""
    pass

class LLMServiceError(ContractAnalyzerError):
    """Raised when LLM service encounters an error."""
    pass

class StorageError(ContractAnalyzerError):
    """Raised when storage operations fail."""
    pass

class ValidationError(ContractAnalyzerError):
    """Raised when validation fails."""
    pass