"""
Developer Agent - Writes actual code
"""
import logging
from typing import Dict, Any
from groq_client import groq_client

logger = logging.getLogger(__name__)

class DeveloperAgent:
    """Agent that writes code based on specifications"""
    
    def __init__(self):
        self.system_prompt = """You are a Senior Full-Stack Developer.
        Write clean, production-ready, well-documented code.
        
        RULES:
        1. Write complete, runnable code
        2. Include proper imports
        3. Add error handling
        4. Follow PEP 8 (Python) or equivalent standards
        5. Add docstrings and comments
        6. Make it testable
        
        Return ONLY the code, no explanations, no markdown blocks."""
    
    async def write_file(self, 
                        file_spec: Dict[str, Any], 
                        project_context: Dict[str, Any]) -> str:
        """
        Write code for a specific file
        """
        file_path = file_spec.get("path", "unknown.py")
        file_description = file_spec.get("description", "Code file")
        language = file_spec.get("language", "python")
        
        logger.info(f"Writing file: {file_path}")
        
        prompt = f"""
        FILE TO CREATE: {file_path}
        FILE DESCRIPTION: {file_description}
        PROGRAMMING LANGUAGE: {language}
        
        PROJECT CONTEXT:
        - Name: {project_context.get('project_name', 'Unknown')}
        - Goal: {project_context.get('project_goal', 'No goal provided')}
        
        REQUIREMENTS:
        1. Create a complete, functional file
        2. Handle edge cases and errors
        3. Include necessary imports
        4. Add type hints if applicable
        5. Include a main guard if appropriate
        
        For Python files:
        - Use f-strings for string formatting
        - Add logging
        - Use pathlib for file paths
        - Follow FastAPI patterns if it's an API
        
        Write the COMPLETE code now:
        """
        
        try:
            code = await groq_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.2,
                max_tokens=2000
            )
            
            # Clean up the response
            code = code.strip()
            
            # Remove markdown code blocks if present
            if code.startswith("```"):
                lines = code.split('\n')
                if len(lines) > 1:
                    # Remove first and last line if they are ```
                    if lines[0].startswith("```") and lines[-1].startswith("```"):
                        code = '\n'.join(lines[1:-1])
                    elif lines[0].startswith("```"):
                        code = '\n'.join(lines[1:])
            
            logger.info(f"Generated {len(code)} characters for {file_path}")
            return code
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise