# app/core/report.py
from typing import Dict, List
from datetime import datetime
from app.services.llm import LLMService
from app.models.enums import RegulationType
from app.utils import ReportGenerationError, logger

class ReportGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_report(
        self,
        file_path: str,
        clauses: List[Dict],
        compliance_results: Dict,
        regulations: List[RegulationType]
    ) -> Dict:
        """Generate comprehensive compliance report."""
        try:
            return {
                "file_name": file_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "regulations": [reg.value for reg in regulations],
                "clauses": clauses,
                "compliance_results": compliance_results,
                "summary": self._generate_summary(clauses, compliance_results, regulations)
            }
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ReportGenerationError(f"Failed to generate report: {str(e)}")

    def _generate_summary(
        self,
        clauses: List[Dict],
        compliance_results: Dict,
        regulations: List[RegulationType]
    ) -> Dict:
        """Generate comprehensive summary of findings."""
        try:
            # Initialize summary
            summary = {
                "total_clauses": len(clauses),
                "analyzed_regulations": [reg.value for reg in regulations],
                "timestamp": datetime.now().isoformat(),
                "overall_compliance": self._calculate_overall_compliance(compliance_results),
                "risk_distribution": self._calculate_risk_distribution(compliance_results),
                "category_analysis": self._analyze_categories(clauses),
                "critical_findings": self._extract_critical_findings(compliance_results),
                "key_actions_required": self._extract_key_actions(compliance_results)
            }
            return summary

        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {
                "total_clauses": len(clauses),
                "analyzed_regulations": [reg.value for reg in regulations],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _calculate_overall_compliance(self, compliance_results: Dict) -> Dict:
        """Calculate overall compliance metrics."""
        total = 0
        compliant = 0
        
        for clause_results in compliance_results.values():
            for reg_result in clause_results.values():
                total += 1
                if reg_result.get("compliant", False):
                    compliant += 1
        
        return {
            "compliant_clauses": compliant,
            "non_compliant_clauses": total - compliant,
            "compliance_percentage": round((compliant / total * 100) if total > 0 else 0, 2)
        }

    def _calculate_risk_distribution(self, compliance_results: Dict) -> Dict:
        """Calculate risk level distribution."""
        risk_counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for clause_results in compliance_results.values():
            for reg_result in clause_results.values():
                risk_level = reg_result.get("risk_level", "high").lower()
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        return risk_counts

    def _analyze_categories(self, clauses: List[Dict]) -> Dict:
        """Analyze clause categories."""
        categories = {}
        for clause in clauses:
            category = clause.get("primary_category", "other")
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "distribution": categories,
            "primary_concerns": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    def _extract_critical_findings(self, compliance_results: Dict) -> List[str]:
        """Extract critical findings from high-risk items."""
        critical_findings = []
        for clause_results in compliance_results.values():
            for reg_result in clause_results.values():
                if reg_result.get("risk_level") == "high":
                    findings = reg_result.get("findings", [])
                    critical_findings.extend(findings)
        
        # Remove duplicates and limit to most critical
        return list(set(critical_findings))[:5]

    def _extract_key_actions(self, compliance_results: Dict) -> List[str]:
        """Extract key recommended actions."""
        actions = []
        for clause_results in compliance_results.values():
            for reg_result in clause_results.values():
                if reg_result.get("risk_level") == "high":
                    recommendations = reg_result.get("recommendations", [])
                    actions.extend(recommendations)
        
        # Remove duplicates and limit to most important
        return list(set(actions))[:5]