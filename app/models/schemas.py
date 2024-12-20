# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from .enums import RegulationType, ClauseCategory

class ContractAnalysisRequest(BaseModel):
    """Request model for contract analysis."""
    regulations: List[RegulationType] = Field(
        ..., 
        description="List of regulations to check compliance against"
    )

class ClauseAnalysis(BaseModel):
    """Model for analyzed clause data."""
    id: str
    text: str
    primary_category: str
    secondary_categories: List[str] = Field(default_factory=list)
    obligations: List[str] = Field(default_factory=list)
    deadlines: List[str] = Field(default_factory=list)
    compliance_risks: List[str] = Field(default_factory=list)
    risk_score: float = Field(default=5.0)

class ComplianceResult(BaseModel):
    """Model for compliance analysis results."""
    compliant: bool = Field(default=False)
    requirements_met: List[str] = Field(default_factory=list)
    requirements_missing: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="high")
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class AnalysisReport(BaseModel):
    """Model for complete analysis report."""
    file_name: str
    analysis_timestamp: datetime
    regulations: List[RegulationType]
    clauses: List[ClauseAnalysis]
    compliance_results: Dict[str, Dict[str, ComplianceResult]]
    summary: Dict[str, Any]

    class Config:
        """Pydantic config for the model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthCheckResponse(BaseModel):
    """Model for API health check response."""
    status: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Model for API error responses."""
    detail: str
    error_code: Optional[str] = None