# app/core/analyzer.py
from typing import List, Dict
from app.core.parser import ContractParser
from app.core.compliance import ComplianceAnalyzer
from app.core.report import ReportGenerator
from app.models.schemas import AnalysisReport, ClauseAnalysis, ComplianceResult
from app.models.enums import RegulationType
from app.services.llm import LLMService
from app.utils import AnalysisError, logger
from datetime import datetime

class ContractAnalyzer:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.parser = ContractParser()
        self.compliance_analyzer = ComplianceAnalyzer(llm_service)
        self.report_generator = ReportGenerator(llm_service)

    async def analyze_contract(
        self,
        file_path: str,
        regulations: List[RegulationType]
    ) -> Dict:
        try:
            logger.info(f"Starting analysis for {file_path}")
            
            # Parse contract
            contract_text = self.parser.parse(file_path)
            
            # Extract clauses
            raw_clauses = await self.compliance_analyzer.extract_clauses(contract_text)
            
            # Convert to ClauseAnalysis objects
            clauses = []
            for clause in raw_clauses:
                clause_model = ClauseAnalysis(
                    id=clause["id"],
                    text=clause["text"],
                    primary_category=clause["primary_category"],
                    secondary_categories=clause["secondary_categories"],
                    obligations=clause["obligations"],
                    deadlines=clause["deadlines"],
                    compliance_risks=clause["compliance_risks"],
                    risk_score=5.0
                )
                clauses.append(clause_model)
            
            # Analyze compliance for each clause
            compliance_results = {}
            for clause in clauses:
                clause_results = {}
                for regulation in regulations:
                    try:
                        # Convert Pydantic model to dict for analysis
                        clause_data = {
                            "text": clause.text,
                            "primary_category": clause.primary_category,
                            "secondary_categories": clause.secondary_categories,
                            "obligations": clause.obligations,
                            "deadlines": clause.deadlines,
                            "compliance_risks": clause.compliance_risks
                        }
                        
                        reg_result = await self.compliance_analyzer.analyze_compliance(
                            clause_data,
                            [regulation]
                        )

                        reg_data = reg_result.get(regulation.value, {})
                        
                        # Create ComplianceResult
                        compliance_result = ComplianceResult(
                            compliant=reg_data.get("compliant", False),
                            requirements_met=reg_data.get("requirements_met", []),
                            requirements_missing=reg_data.get("requirements_missing", []),
                            risk_level=reg_data.get("risk_level", "high"),
                            findings=reg_data.get("findings", []),
                            recommendations=reg_data.get("recommendations", [])
                        )
                        clause_results[regulation.value] = compliance_result
                    except Exception as e:
                        logger.error(f"Failed to analyze {regulation.value}: {str(e)}")
                        clause_results[regulation.value] = ComplianceResult()

                compliance_results[clause.id] = clause_results

            # Generate the summary using the report generator
            summary = await self.report_generator.generate_report(
                file_path=file_path,
                clauses=[c.model_dump() for c in clauses],  # Convert clauses to dict
                compliance_results={
                    k: {
                        reg: cr.model_dump() 
                        for reg, cr in v.items()
                    } 
                    for k, v in compliance_results.items()
                },  # Convert compliance results to dict
                regulations=regulations
            )

            # Create the final report
            report = AnalysisReport(
                file_name=file_path,
                analysis_timestamp=datetime.now(),
                regulations=regulations,
                clauses=clauses,
                compliance_results=compliance_results,
                summary=summary
            )
            
            return report.model_dump()
            
        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {str(e)}")
            raise AnalysisError(f"Contract analysis failed: {str(e)}")