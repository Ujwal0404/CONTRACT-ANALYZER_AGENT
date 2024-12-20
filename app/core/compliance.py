# app/core/compliance.py
from typing import Dict, List, Optional, Any
from app.models.enums import RegulationType, ClauseCategory
from app.models.schemas import ComplianceResult
from app.services.llm import LLMService
from app.utils import ComplianceError, logger
import uuid
import json
import re
from functools import lru_cache

class ComplianceAnalyzer:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.setup_prompts()
        self._clause_cache = {}

    def setup_prompts(self):
        """Set up the prompts for the analysis."""
        self.extraction_prompt = """Analyze the contract below and extract its clauses.

Output Format:
{
    "clauses": [
        {
            "text": "The actual clause text",
            "primary_category": "choose from categories below",
            "secondary_categories": ["array", "of", "categories"],
            "obligations": ["list", "of", "obligations"],
            "deadlines": ["list", "of", "deadlines"],
            "compliance_risks": ["list", "of", "risks"]
        }
    ]
}

Categories: data_privacy, security, liability, termination, payment, confidentiality, intellectual_property, compliance, force_majeure, dispute_resolution

Contract:
{text}"""

        self.compliance_prompt = """You are a compliance expert. Analyze the following clause for {regulation} compliance.

Clause Details:
Primary Category: {primary_category}
Secondary Categories: {secondary_categories}
Obligations:
{obligations}
Deadlines:
{deadlines}
Identified Compliance Risks:
{compliance_risks}

Complete Clause Text:
{text}

Analyze considering:
1. The appropriateness of the categorization
2. The completeness of obligations
3. The accuracy of identified risks
4. Specific {regulation} requirements
5. Deadlines and timing requirements

Provide your analysis in this exact JSON format:
{{
    "compliant": false,
    "requirements_met": [
        "List specific requirements that are met"
    ],
    "requirements_missing": [
        "List specific missing requirements"
    ],
    "risk_level": "high/medium/low",
    "findings": [
        "List detailed findings considering all provided context"
    ],
    "recommendations": [
        "List specific, actionable recommendations"
    ]
}}

Return ONLY the JSON object. Use only "high", "medium", or "low" for risk_level."""


    @lru_cache(maxsize=100)
    def _get_clause_hash(self, text: str) -> str:
        """Generate hash for clause text."""
        return str(hash(text))

    async def extract_clauses(self, contract_text: str) -> List[Dict]:
        """Extract clauses from contract text."""
        try:
            # Check cache
            cache_key = self._get_clause_hash(contract_text)
            if cache_key in self._clause_cache:
                logger.info("Using cached clause extraction")
                return self._clause_cache[cache_key]

            logger.info("Generating clause extraction response")
            response = await self.llm.generate(
                self.extraction_prompt + contract_text
            )
            
            if not response:
                raise ComplianceError("Empty response from LLM")

            cleaned_json = self._clean_json_response(response)
            if not cleaned_json:
                raise ComplianceError("Failed to extract valid JSON from response")

            data = self._parse_json_with_fallbacks(cleaned_json)
            if not data:
                raise ComplianceError("Failed to parse response as JSON")

            clauses = self._extract_clauses_from_data(data)
            if not clauses:
                raise ComplianceError("No valid clauses found in response")

            # Cache results
            self._clause_cache[cache_key] = clauses
            logger.info(f"Successfully extracted {len(clauses)} clauses")
            return clauses

        except Exception as e:
            logger.error(f"Clause extraction failed: {str(e)}")
            raise ComplianceError(str(e))
        
    async def analyze_compliance(
        self,
        clause: Dict[str, Any],
        regulations: List[RegulationType]
    ) -> Dict[str, Any]:
        """Analyze clause compliance against multiple regulations."""
        try:
            results = {}
            for regulation in regulations:
                try:
                    logger.debug(f"Analyzing {regulation.value} compliance")
                    results[regulation.value] = await self._analyze_single_regulation(
                        clause,
                        regulation
                    )
                except Exception as e:
                    logger.error(f"Failed to analyze {regulation.value}: {str(e)}")
                    results[regulation.value] = self._get_default_result()

            return results

        except Exception as e:
            logger.error(f"Compliance analysis failed: {str(e)}")
            return {reg.value: self._get_default_result() for reg in regulations}

    async def _analyze_single_regulation(
        self,
        clause: Dict[str, Any],
        regulation: RegulationType
    ) -> Dict[str, Any]:
        """Analyze compliance against a single regulation."""
        try:
            # Format the prompt with all clause information
            formatted_prompt = self.compliance_prompt.format(
                regulation=regulation.value,
                text=clause.get("text", ""),
                primary_category=clause.get("primary_category", ""),
                secondary_categories=", ".join(clause.get("secondary_categories", [])),
                obligations="\n".join(f"- {o}" for o in clause.get("obligations", [])),
                deadlines="\n".join(f"- {d}" for d in clause.get("deadlines", [])),
                compliance_risks="\n".join(f"- {r}" for r in clause.get("compliance_risks", []))
            )
            
            response = await self.llm.generate(formatted_prompt)
            cleaned_response = self._extract_json_from_response(response)
            
            if not cleaned_response:
                raise ValueError("No valid JSON found in response")

            result = json.loads(cleaned_response)
            
            return {
                "compliant": bool(result.get("compliant", False)),
                "requirements_met": result.get("requirements_met", []),
                "requirements_missing": result.get("requirements_missing", []),
                "risk_level": self._validate_risk_level(result.get("risk_level", "high")),
                "findings": result.get("findings", []),
                "recommendations": result.get("recommendations", [])
            }

        except Exception as e:
            logger.error(f"Regulation analysis failed for {regulation.value}: {str(e)}")
            return self._get_default_result()

    # async def analyze_compliance(
    #     self,
    #     clause: Dict[str, str],
    #     regulations: List[RegulationType]
    # ) -> Dict[str, Any]:
    #     """Analyze clause compliance against multiple regulations."""
    #     try:
    #         # Cache key for compliance results
    #         cache_key = f"{self._get_clause_hash(clause['text'])}_{','.join(sorted([r.value for r in regulations]))}"
            
    #         # Check cache
    #         if cache_key in self._clause_cache:
    #             return self._clause_cache[cache_key]

    #         results = {}
    #         for regulation in regulations:
    #             try:
    #                 logger.debug(f"Analyzing {regulation.value} compliance")
    #                 results[regulation.value] = await self._analyze_single_regulation(
    #                     clause["text"],
    #                     regulation
    #                 )
    #             except Exception as e:
    #                 logger.error(f"Failed to analyze {regulation.value}: {str(e)}")
    #                 results[regulation.value] = self._get_default_result()

    #         # Cache results
    #         self._clause_cache[cache_key] = results
    #         return results

    #     except Exception as e:
    #         logger.error(f"Compliance analysis failed: {str(e)}")
    #         return {reg.value: self._get_default_result() for reg in regulations}


    def _clean_json_response(self, response: str) -> Optional[str]:
        """Clean and extract JSON from response."""
        if not response or not isinstance(response, str):
            return None

        try:
            # Remove any non-printable characters
            response = ''.join(char for char in response if char.isprintable() or char in ['\n', '\r', '\t'])
            
            # Try to find JSON structure
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match and '"clauses"' in json_match.group(0):
                return json_match.group(0)

            # Try finding array structure
            array_match = re.search(r'\[([\s\S]*)\]', response)
            if array_match:
                return f'{{"clauses": {array_match.group(0)}}}'

            return None

        except Exception as e:
            logger.error(f"JSON cleaning failed: {str(e)}")
            return None

    def _parse_json_with_fallbacks(self, json_str: str) -> Optional[Dict]:
        """Parse JSON with multiple fallback attempts."""
        try:
            # First attempt: direct parsing
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.debug("Direct JSON parsing failed, trying cleanup")

            # Second attempt: clean and retry
            cleaned = json_str.replace('\n', ' ').replace('\r', '')
            cleaned = re.sub(r'"\s*:\s*"', '": "', cleaned)
            cleaned = re.sub(r'"\s*:\s*\[', '": [', cleaned)
            cleaned = re.sub(r'\]\s*,\s*"', '], "', cleaned)
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.debug("Cleaned JSON parsing failed, trying reconstruction")

            # Third attempt: reconstruct
            clauses_content = re.findall(r'\{[^{}]*\}', cleaned)
            if clauses_content:
                reconstructed = {"clauses": []}
                for clause in clauses_content:
                    try:
                        clause_obj = json.loads(clause)
                        reconstructed["clauses"].append(clause_obj)
                    except:
                        continue
                if reconstructed["clauses"]:
                    return reconstructed

            return None

        except Exception as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return None

    def _extract_clauses_from_data(self, data: Dict) -> List[Dict]:
        """Extract and validate clauses from parsed data."""
        try:
            clauses = data.get("clauses", [])
            if isinstance(clauses, dict):
                clauses = [clauses]
            elif not isinstance(clauses, list):
                raise ValueError("Invalid clauses format")

            valid_clauses = []
            for clause in clauses:
                processed = self._process_clause(clause)
                if processed:
                    valid_clauses.append(processed)

            return valid_clauses

        except Exception as e:
            logger.error(f"Clause extraction failed: {str(e)}")
            return []

    def _process_clause(self, clause: Dict) -> Optional[Dict]:
        """Process and validate a single clause."""
        try:
            text = self._clean_text(clause.get("text", ""))
            if not text:
                return None

            return {
                "id": str(uuid.uuid4()),
                "text": text,
                "primary_category": self._validate_category(clause.get("primary_category", "other")),
                "secondary_categories": self._process_list(
                    clause.get("secondary_categories", []),
                    self._validate_category
                ),
                "obligations": self._process_list(
                    clause.get("obligations", []),
                    self._clean_text
                ),
                "deadlines": self._process_list(
                    clause.get("deadlines", []),
                    self._clean_text
                ),
                "compliance_risks": self._process_list(
                    clause.get("compliance_risks", []),
                    self._clean_text
                )
            }
        except Exception as e:
            logger.warning(f"Clause processing failed: {str(e)}")
            return None

    # async def analyze_compliance(
    #     self,
    #     clause: Dict[str, str],
    #     regulations: List[RegulationType]
    # ) -> Dict[str, Any]:
    #     """Analyze clause compliance against multiple regulations."""
    #     try:
    #         results = {}
    #         for regulation in regulations:
    #             try:
    #                 logger.debug(f"Analyzing {regulation.value} compliance")
    #                 results[regulation.value] = await self._analyze_single_regulation(
    #                     clause["text"],
    #                     regulation
    #                 )
    #             except Exception as e:
    #                 logger.error(f"Failed to analyze {regulation.value}: {str(e)}")
    #                 results[regulation.value] = self._get_default_result()

    #         return results

    #     except Exception as e:
    #         logger.error(f"Compliance analysis failed: {str(e)}")
    #         return {reg.value: self._get_default_result() for reg in regulations}

    # async def _analyze_single_regulation(
    #     self,
    #     clause_text: str,
    #     regulation: RegulationType
    # ) -> Dict[str, Any]:
    #     """Analyze compliance against a single regulation."""
    #     try:
    #         prompt = self.compliance_prompt.format(
    #             regulation=regulation.value,
    #             clause=clause_text
    #         )
    #         print(prompt, "COMPLIANCE PROMPT")
            
    #         response = await self.llm.generate(prompt)
    #         cleaned_response = self._extract_json_from_response(response)
            
    #         if not cleaned_response:
    #             raise ValueError("No valid JSON found in response")

    #         result = json.loads(cleaned_response)
            
    #         return {
    #             "compliant": bool(result.get("compliant", False)),
    #             "requirements_met": result.get("requirements_met", []),
    #             "requirements_missing": result.get("requirements_missing", []),
    #             "risk_level": self._validate_risk_level(result.get("risk_level", "high")),
    #             "findings": result.get("findings", []),
    #             "recommendations": result.get("recommendations", [])
    #         }

    #     except Exception as e:
    #         logger.error(f"Regulation analysis failed for {regulation.value}: {str(e)}")
    #         return self._get_default_result()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ""
        return ' '.join(text.split()).strip()

    def _validate_category(self, category: str) -> str:
        """Validate and normalize category names."""
        if not category:
            return "other"
        
        category = self._clean_text(str(category)).lower().replace(" ", "_")
        valid_categories = {item.value for item in ClauseCategory}
        
        return category if category in valid_categories else "other"

    def _process_list(self, items: list, processor_func) -> List[str]:
        """Process list items with given function."""
        if not items or not isinstance(items, list):
            return []
        
        processed = []
        for item in items:
            try:
                processed_item = processor_func(item)
                if processed_item:
                    processed.append(processed_item)
            except Exception:
                continue
                
        return processed

    def _validate_risk_level(self, risk_level: str) -> str:
        """Validate risk level value."""
        if not isinstance(risk_level, str):
            return "high"
        
        risk_level = risk_level.lower().strip()
        valid_levels = ["high", "medium", "low"]
        
        return risk_level if risk_level in valid_levels else "high"

    def _get_default_result(self) -> Dict[str, Any]:
        """Get default result for error cases."""
        return {
            "compliant": False,
            "requirements_met": [],
            "requirements_missing": ["Analysis failed"],
            "risk_level": "high",
            "findings": ["Unable to analyze clause"],
            "recommendations": ["Perform manual review"]
        }


    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extract valid JSON from LLM response."""
        if not response or not isinstance(response, str):
            return None

        try:
            # Clean response first
            response = self._clean_response(response)
            
            # Method 1: Find complete JSON object
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    potential_json = json_match.group(0)
                    # Verify it can be parsed
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass

            # Method 2: Find JSON array
            array_match = re.search(r'\[[\s\S]*\]', response)
            if array_match:
                try:
                    potential_json = array_match.group(0)
                    # Verify it can be parsed
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass

            # Method 3: Try to extract individual JSON objects
            objects = re.findall(r'\{[^{}]*\}', response)
            if objects:
                # For single object, return first valid JSON
                for obj in objects:
                    try:
                        json.loads(obj)
                        return obj
                    except json.JSONDecodeError:
                        continue

            return None

        except Exception as e:
            logger.error(f"JSON extraction failed: {str(e)}\nResponse: {response[:200]}")
            return None

    def _clean_response(self, response: str) -> str:
        """Clean and normalize LLM response."""
        if not response:
            return ""
            
        # Remove non-printable characters except newlines and spaces
        response = ''.join(char for char in response if char.isprintable() or char in ['\n', ' '])
        
        # Normalize quotes
        response = response.replace('"', '"').replace('"', '"')
        
        # Remove any markdown code block indicators
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        return response

