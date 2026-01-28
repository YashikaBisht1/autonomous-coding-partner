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
                           tech_stack: List[str] = None,
                           websocket_callback = None) -> ProjectState:
        """
        Create a new project using all agents
        """
        # Initialize project state
        project_state = ProjectState(project_id, project_name, goal, tech_stack)
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
            
            # Pass tech stack if provided in project_data (we need to update Main as well)
            tech_stack = getattr(project_state, 'tech_stack', None)
            plan = await self.planner.create_plan(goal, project_name, tech_stack)
            project_state.add_log("planning", "Project plan created", {"tasks_count": len(plan.get("tasks", []))})
            
            # Step 2: Development
            project_state.update_status(ProjectStatus.CODING)
            update_progress("coding", f"Generating {len(plan.get('files', []))} files...")
            
            primary_language = "python"
            for file_spec in plan.get("files", []):
                file_path = file_spec.get("path")
                lang = file_spec.get("language", "python").lower()
                if lang != "markdown":
                    primary_language = lang
                update_progress("coding", f"Creating file: {file_path} ({lang})")
                
                # Generate code
                code = await self.developer.write_file(file_spec, plan)
                
                # Save file
                await file_manager.save_file(project_id, file_path, code)
                project_state.add_file(file_path)
                project_state.add_log("file_created", f"Created file: {file_path}", {"size": len(code)})

            # Step 2.5: Dependency Installation
            dependencies = plan.get("dependencies", [])
            if dependencies:
                update_progress("dependencies", f"Installing dependencies: {', '.join(dependencies)}")
                await self._install_dependencies(project_id, dependencies, primary_language)
            
            # Step 3: Testing & Fixing (Iterative Loop)
            project_state.update_status(ProjectStatus.TESTING)
            update_progress("testing", f"Testing {primary_language.capitalize()} project...")
            
            # For each generated file, try to test and fix it
            for file_path in project_state.files:
                # Detect language for this specific file
                file_lang = "python"
                for f in plan.get("files", []):
                    if f["path"] == file_path:
                        file_lang = f.get("language", "python").lower()
                        break
                
                if file_lang == "markdown" or file_path.startswith("test_"):
                    continue
                    
                # Read generated code
                code = await file_manager.read_file(project_id, file_path)
                
                # Generate tests
                update_progress("testing", f"Creating tests for {file_path}...")
                test_code = await self.tester.create_tests(code, file_path, {"language": file_lang})
                
                # File naming convention for tests
                ext = file_path.split('.')[-1]
                test_file_name = f"test_{file_path.replace('.' + ext, '')}.{ext}" if file_lang == 'python' else f"{file_path.replace('.' + ext, '')}.test.{ext}"
                
                await file_manager.save_file(project_id, test_file_name, test_code)
                
                # Execute tests
                workspace_path = file_manager.get_project_dir(project_id)
                test_result = await self.tester.run_test_file(test_file_name, workspace_path, file_lang)
                
                if test_result["success"]:
                    update_progress("testing", f"✅ Tests passed for {file_path}")
                    project_state.add_log("test_success", f"Tests passed for {file_path}")
                else:
                    # FIX LOOP (Maximum 2 attempts for now)
                    for attempt in range(2):
                        update_progress("fixing", f"🔧 Tests failed for {file_path}. Attempting fix {attempt+1}/2...")
                        project_state.add_log("test_failure", f"Tests failed for {file_path}", {"error": test_result["error"]})
                        
                        # Fix code
                        fixed_code = await self.fixer.fix_code(code, test_result["error"], file_path, file_lang)
                        await file_manager.save_file(project_id, file_path, fixed_code)
                        code = fixed_code # Update for next attempt if needed
                        
                        # Re-run tests
                        test_result = await self.tester.run_test_file(test_file_name, workspace_path, file_lang)
                        if test_result["success"]:
                            update_progress("fixing", f"✅ Fixed {file_path} successfully!")
                            break
                    
                    if not test_result["success"]:
                        update_progress("warning", f"⚠️ Could not fix all issues in {file_path}")

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

    async def _install_dependencies(self, project_id: str, dependencies: List[str], language: str):
        """Install tech stack dependencies"""
        workspace_path = file_manager.get_project_dir(project_id)
        if language == "python":
            cmd = ["pip", "install"] + dependencies
        elif language in ["javascript", "typescript"]:
            # Check if package.json exists, if not init
            pkg_json = workspace_path / "package.json"
            if not pkg_json.exists():
                import subprocess
                subprocess.run(["npm", "init", "-y"], cwd=workspace_path)
            cmd = ["npm", "install"] + dependencies
        else:
            logger.warning(f"Dependency installation not supported for {language}")
            return

        logger.info(f"Installing dependencies for {project_id}: {cmd}")
        import subprocess
        try:
            subprocess.run(cmd, cwd=workspace_path, capture_output=True, text=True, timeout=120)
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
    
    def get_project_state(self, project_id: str) -> ProjectState:
        """Get current project state"""
        return self.active_projects.get(project_id)