"""
Saboteur Agent - Injects subtle, logical bugs for debugging challenges
"""
import logging
from typing import Dict, Any, List
from groq_client import groq_client

logger = logging.getLogger(__name__)

class SaboteurAgent:
    """Agent that sabotages working code for training and challenges"""
    
    def __init__(self):
        self.system_prompt = """You are a Malicious Senior Software Engineer.
        Your goal is to take perfectly working code and inject ONE SUBTLE, LOGICAL BUG for a developer challenge.
        
        RULES:
        1. Only inject ONE bug per file.
        2. The bug must be logical (e.g., off-by-one, wrong sign, boundary condition, incorrect sorting logic).
        3. Do NOT make syntax errors. The code must compile/run.
        4. The bug should be hard to spot with just a quick glance.
        5. Do not change the function signatures or imports.
        
        OUTPUT_FORMAT (JSON):
        {
            "sabotaged_code": "The full code with the bug",
            "mission_hint": "A cryptic, cyberpunk-style hint about the system failure",
            "intel": "Technical description of the bug for system logs"
        }"""
    
    async def sabotage_file(self, original_code: str, file_path: str, language: str = "python") -> Dict[str, Any]:
        """
        Inject a subtle bug into a file
        """
        logger.info(f"Sabotaging file for challenge: {file_path}")
        
        prompt = f"""
        ORIGINAL_CODE ({language}):
        {original_code}
        
        TASK:
        Inject a subtle, realistic logic bug that will break a unit test but look correct to a junior developer.
        Return the JSON structure with sabotaged_code, mission_hint, and intel.
        """
        
        try:
            response = await groq_client.generate_structured(
                prompt=prompt,
                system_prompt=self.system_prompt,
                json_format=True
            )
            
            # groq_client handles markdown stripping, so we can use response directly
            return response
        except Exception as e:
            logger.error(f"Error sabotaging file: {e}")
            raise
