"""
Planner Agent - Breaks down project requirements into tasks
"""
import json
import logging
from typing import Dict, Any, List
from groq_client import groq_client

logger = logging.getLogger(__name__)

class PlannerAgent:
    """Agent that plans project structure and tasks"""
    
    def __init__(self):
        self.system_prompt = """You are a Senior Software Architect with 15+ years of experience.
        Break down project requirements into actionable development tasks.
        
        CRITICAL: Return ONLY valid JSON, no other text.
        
        Output Format:
        {
            "tasks": ["task1", "task2", ...],
            "files": [
                {
                    "path": "path/to/file.py",
                    "description": "what this file does",
                    "language": "python"
                }
            ],
            "dependencies": ["package1", "package2"],
            "test_files": ["test_file1.py", ...],
            "estimated_time": "2 hours"
        }"""
    
    async def create_plan(self, project_goal: str, project_name: str, tech_stack: List[str] = None) -> Dict[str, Any]:
        """
        Create a detailed project plan
        """
        logger.info(f"Planning project: {project_name}")
        stack_str = ", ".join(tech_stack) if tech_stack else "Python (Default)"
        
        prompt = f"""
        PROJECT NAME: {project_name}
        PROJECT GOAL: {project_goal}
        PREFERRED TECH STACK: {stack_str}
        
        Create a complete development plan with:
        
        1. TASKS: List of specific, actionable tasks in correct order
        2. FILES: Complete file structure with descriptions. Ensure 'language' field matches the tech stack.
        3. DEPENDENCIES: Packages needed for the chosen stack.
        4. TEST_FILES: Test files to create.
        5. ESTIMATED_TIME: Realistic time estimate
        
        Focus on main functionality first, then error handling and testing.
        """
        
        try:
            plan = await groq_client.generate_structured(
                prompt=prompt,
                system_prompt=self.system_prompt,
                json_format=True
            )
            
            # Validate and enhance plan
            if not isinstance(plan, dict) or "error" in plan or not plan.get("files"):
                logger.warning(f"Invalid or empty plan from API, using fallback. Plan: {plan}")
                return self._get_fallback_plan(project_name, project_goal)
            
            # Ensure required fields
            plan.setdefault("tasks", [])
            plan.setdefault("files", [])
            plan.setdefault("dependencies", [])
            plan.setdefault("test_files", [])
            plan.setdefault("estimated_time", "1 hour")
            
            # Add project metadata
            plan["project_name"] = project_name
            plan["project_goal"] = project_goal
            
            logger.info(f"Created plan with {len(plan['tasks'])} tasks and {len(plan['files'])} files")
            return plan
            
        except Exception as e:
            logger.error(f"Error in planning: {e}")
            return self._get_fallback_plan(project_name, project_goal, str(e))

    def _get_fallback_plan(self, project_name: str, project_goal: str, error: str = None) -> Dict[str, Any]:
        """Return a basic plan as fallback"""
        return {
            "project_name": project_name,
            "project_goal": project_goal,
            "tasks": [
                "Create project structure",
                "Write main application file",
                "Add basic functionality",
                "Create README documentation"
            ],
            "files": [
                {
                    "path": "main.py",
                    "description": "Main application file",
                    "language": "python"
                },
                {
                    "path": "README.md",
                    "description": "Project documentation",
                    "language": "markdown"
                }
            ],
            "dependencies": [],
            "test_files": [],
            "estimated_time": "1 hour",
            "error": error
        }