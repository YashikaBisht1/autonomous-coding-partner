import logging
import subprocess
import os
import tempfile
from groq_client import GroqClient

logger = logging.getLogger(__name__)

class TesterAgent:
    def __init__(self):
        self.groq_client = GroqClient()
        self.prompts = {
            "python": "You are an expert QA Engineer. Generate robust Python unit tests using 'unittest' or 'pytest'.",
            "javascript": "You are an expert QA Engineer. Generate robust Node.js tests using 'jest' or 'mocha'.",
            "typescript": "You are an expert QA Engineer. Generate robust TypeScript tests using 'jest' or 'vitest'.",
            "go": "You are an expert QA Engineer. Generate robust Go tests using the 'testing' package."
        }
        self.test_commands = {
            "python": ["python", "-m", "unittest"],
            "javascript": ["npm", "test"],
            "typescript": ["npm", "test"],
            "go": ["go", "test"]
        }

    async def create_tests(self, code: str, file_path: str, context: dict) -> str:
        """Generate test code for a given file"""
        language = context.get("language", "python").lower()
        system_prompt = self.prompts.get(language, self.prompts["python"])
        
        prompt = f"""Generate a comprehensive test for the following code:
File: {file_path}
Language: {language}
Code:
{code}

Include edge cases and error handling tests.
Return ONLY valid {language} code. No markdown, no explanations."""
        
        code = await self.groq_client.generate(prompt, system_prompt=system_prompt)
        
        # Clean up the response
        code = code.strip()
        if code.startswith("```"):
            lines = code.split('\n')
            if len(lines) > 1 and lines[0].startswith("```"):
                code = '\n'.join(lines[1:])
            if code.endswith("```"):
                code = code[:-3]
                
        return code.strip()

    async def run_test_file(self, test_file_path: str, workspace_dir: str, language: str = "python") -> dict:
        """Execute a test file and return the output/status"""
        language = language.lower()
        base_cmd = self.test_commands.get(language, self.test_commands["python"])
        
        # Adjust command for language
        if language == "python":
            cmd = base_cmd + [os.path.basename(test_file_path)]
        else:
            # For JS/Go, they often scan the directory or have specific flags
            cmd = base_cmd
            
        logger.info(f"Running tests: {cmd} in {workspace_dir}")
        try:
            result = subprocess.run(
                cmd,
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=60 # Increased timeout for npm install/test
            )
            
            success = result.returncode == 0
            return {
                "success": success,
                "output": result.stdout,
                "error": result.stderr if not success else None,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test execution timed out", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

