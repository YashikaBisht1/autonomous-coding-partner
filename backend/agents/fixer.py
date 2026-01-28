"""
Fixer Agent - Fixes bugs in code
"""
import logging
from typing import Dict, Any
from groq_client import GroqClient

logger = logging.getLogger(__name__)

class FixerAgent:
    """Agent that fixes bugs and errors"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.system_prompt = """You are a Senior Debugging Engineer.
        Fix bugs and errors in code based on test failures.
        
        RULES:
        1. Understand the error first
        2. Fix the root cause, not symptoms
        3. Maintain code quality
        4. Don't break existing functionality
        5. Add comments explaining the fix
        
        Return ONLY the fixed code, no explanations."""
    
    async def fix_code(self, 
                      original_code: str, 
                      error_message: str,
                      file_path: str) -> str:
        """
        Fix code based on error message
        """
        logger.info(f"Fixing code for: {file_path}")
        
        prompt = f"""
        FIX CODE FOR FILE: {file_path}
        
        ORIGINAL CODE:
        {original_code[:3000]}
        
        ERROR MESSAGE:
        {error_message}
        
        Fix the code to resolve this error.
        Maintain the original functionality.
        Add comments to explain your fix.
        """
        
        try:
            fixed_code = await self.groq_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.1,
                max_tokens=3000
            )
            
            # Clean up the response
            fixed_code = fixed_code.strip()
            if fixed_code.startswith("```"):
                lines = fixed_code.split('\n')
                if len(lines) > 1 and lines[0].startswith("```"):
                    fixed_code = '\n'.join(lines[1:])
                if fixed_code.endswith("```"):
                    fixed_code = fixed_code[:-3]
            
            logger.info(f"Fixed code for {file_path}")
            return fixed_code
            
        except Exception as e:
            logger.error(f"Error fixing code for {file_path}: {e}")
            return original_code  # Return original if fix fails