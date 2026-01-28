import logging
import subprocess
import os
import tempfile
from groq_client import GroqClient

logger = logging.getLogger(__name__)

class TesterAgent:
    def __init__(self):
        self.groq_client = GroqClient()
        self.system_prompt = """You are an expert QA Engineer. 
Your goal is to write robust, comprehensive Python unit tests using the 'unittest' framework.
Always return ONLY the code. No markdown, no explanations."""

    async def create_tests(self, code: str, file_path: str, context: dict) -> str:
        """Generate test code for a given file"""
        prompt = f"""Generate a comprehensive unittest for the following code:
File: {file_path}
Code:
{code}

Include edge cases and error handling tests.
Return ONLY valid Python code."""
        
        return await self.groq_client.generate(prompt, system_prompt=self.system_prompt)

    async def run_test_file(self, test_file_path: str, workspace_dir: str) -> dict:
        """Execute a test file and return the output/status"""
        logger.info(f"Running test file: {test_file_path} in {workspace_dir}")
        try:
            # Run unittest in the workspace directory
            result = subprocess.run(
                ['python', '-m', 'unittest', os.path.basename(test_file_path)],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=30
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

