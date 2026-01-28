"""
Agent Orchestrator - Coordinates all agents
"""
import logging
from typing import Dict, Any, List
from agents.planner import PlannerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent
from agents.fixer import FixerAgent
from services.file_manager import file_manager
from models.project import ProjectState, ProjectStatus

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates all agents to work together"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.developer = DeveloperAgent()
        self.tester = TesterAgent()
        self.fixer = FixerAgent()
        self.active_projects: Dict[str, ProjectState] = {}
    
    async def create_project(self, 
                           project_id: str, 
                           project_name: str, 
                           goal: str,
                           websocket_callback = None) -> ProjectState:
        """
        Create a new project using all agents
        """
        # Initialize project state
        project_state = ProjectState(project_id, project_name, goal)
        self.active_projects[project_id] = project_state
        
        # Callback for progress updates
        def update_progress(step: str, message: str, data: Dict[str, Any] = None):
            project_state.add_log("progress", message, data)
            if websocket_callback:
                websocket_callback({
                    "type": "progress",
                    "step": step,
                    "message": message,
                    "data": data
                })
        
        try:
            # Step 1: Planning
            project_state.update_status(ProjectStatus.PLANNING)
            update_progress("planning", "Creating project plan...")
            
            plan = await self.planner.create_plan(goal, project_name)
            project_state.add_log("planning", "Project plan created", {"tasks_count": len(plan.get("tasks", []))})
            
            # Step 2: Development
            project_state.update_status(ProjectStatus.CODING)
            update_progress("coding", f"Generating {len(plan.get('files', []))} files...")
            
            for file_spec in plan.get("files", []):
                file_path = file_spec.get("path")
                update_progress("coding", f"Creating file: {file_path}")
                
                # Generate code
                code = await self.developer.write_file(file_spec, plan)
                
                # Save file
                await file_manager.save_file(project_id, file_path, code)
                project_state.add_file(file_path)
                project_state.add_log("file_created", f"Created file: {file_path}", {"size": len(code)})
            
            # Step 3: Testing (optional)
            if plan.get("test_files"):
                project_state.update_status(ProjectStatus.TESTING)
                update_progress("testing", "Running tests...")
                
                # Simple test generation for now
                for file_spec in plan.get("files", []):
                    if file_spec.get("language") == "python":
                        file_content = await file_manager.read_file(project_id, file_spec["path"])
                        tests = await self.tester.create_tests(file_content, file_spec["path"], plan)
                        test_path = f"test_{file_spec['path']}"
                        await file_manager.save_file(project_id, test_path, tests)
            
            # Step 4: Completion
            project_state.update_status(ProjectStatus.COMPLETED)
            update_progress("completed", "Project generation complete!", {
                "files_count": len(project_state.files),
                "project_id": project_id
            })
            
            return project_state
            
        except Exception as e:
            logger.error(f"Error in project creation: {e}")
            project_state.update_status(ProjectStatus.FAILED)
            project_state.add_error(str(e))
            project_state.add_log("error", f"Project failed: {str(e)}")
            
            update_progress("failed", f"Project generation failed: {str(e)}")
            raise
    
    def get_project_state(self, project_id: str) -> ProjectState:
        """Get current project state"""
        return self.active_projects.get(project_id)