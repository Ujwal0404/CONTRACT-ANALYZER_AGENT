# app/services/llm.py
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from app.config import get_settings
from typing import Optional, Dict, Any
from app.utils import LLMServiceError, logger
from tenacity import retry, stop_after_attempt, wait_exponential
import json

class LLMService:
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.MODEL_NAME
        print(model_name, "MODEL NAME")
        try:
            self.llm = ChatGroq(
                api_key=api_key,
                model_name="llama-3.1-8b-instant",#self.model_name,
                temperature=0,
                max_tokens=4096,
                streaming=False
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise LLMServiceError(f"LLM service initialization failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(self, prompt: str) -> str:
        """Generate response from LLM with retry logic."""
        if not prompt:
            raise LLMServiceError("Empty prompt provided")
        # print(prompt,"PROMPT")
        try:
            messages = [
                SystemMessage(content=(
                    "You are a contract analysis assistant. "
                    "Always return responses in valid JSON format. "
                    "Do not include any additional text or explanations."
                )),
                HumanMessage(content=prompt)
            ]
            # print(messages, "MESSAGE")
            
            response = await self.llm.agenerate(messages=[messages])
            # print(response)
            
            if not response or not response.generations:
                raise LLMServiceError("Empty response from LLM")
            
            generated_text = response.generations[0][0].text.strip()
            if not generated_text:
                raise LLMServiceError("Empty text in LLM response")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise LLMServiceError(f"LLM generation failed: {str(e)}")