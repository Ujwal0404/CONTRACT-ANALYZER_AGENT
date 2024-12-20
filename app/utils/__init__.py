import logging
import json
from typing import Dict, Any
from datetime import datetime

# Exception definitions
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

# Utility functions
def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def safe_json_loads(content: str) -> Dict[str, Any]:
    """Safely parse JSON content."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()

def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Split text into chunks for LLM processing."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Initialize logger
logger = logging.getLogger(__name__)
setup_logging()