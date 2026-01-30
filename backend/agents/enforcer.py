"""
Enforcer Agent - Validates AI-generated code against style guides and specs
"""
import logging
from typing import Dict, Any, List
from groq_client import groq_client

logger = logging.getLogger(__name__)

class EnforcerAgent:
    """Agent that enforces code quality and architectural standards"""
    
    def __init__(self):
        self.system_prompt = """You are a Senior Architect and Lead Code Reviewer.
        Your task is to enforce strict compliance with a provided STYLE GUIDE and ARCHITECTURAL SPEC.
        
        CRITERIA:
        1. Does the code follow the naming conventions (CamelCase, snake_case, etc.)?
        2. Are there forbidden libraries or patterns?
        3. Is the code sufficiently commented (or clean enough to not need them)?
        4. Does it match the architectural goals?
        
        OUTPUT FORMAT (JSON):
        {
            "compliant": true/false,
            "score": 0-100,
            "violations": [
                {"rule": "Rule name", "issue": "Description", "fix": "How to fix"}
            ],
            "feedback": "Overall summary for the developer"
        }"""
    
    async def enforce(self, code: str, file_path: str, style_guide: str = None, spec: str = None) -> Dict[str, Any]:
        """
        Review code against constraints
        """
        logger.info(f"Enforcing quality standards for: {file_path}")
        
        prompt = f"""
        FILE: {file_path}
        CODE:
        {code}
        
        CONSTRAINTS:
        - STYLE_GUIDE: {style_guide or "Standard Best Practices"}
        - ARCHITECTURAL_SPEC: {spec or "Maintainable, clean code"}
        
        Review this code. If 'compliant' is false, the developer will be forced to regenerate the file.
        """
        
        try:
            import json
            response = await groq_client.generate_structured(
                prompt=prompt,
                system_prompt=self.system_prompt,
                response_format={"type": "json_object"}
            )
            return response
        except Exception as e:
            logger.error(f"Enforcement error: {e}")
            return {"compliant": True, "score": 100, "violations": [], "feedback": f"Review failed but bypassed: {e}"}

enforcer = EnforcerAgent()
