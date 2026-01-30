"""
Agent Orchestrator - Coordinates all agents
"""
import logging
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from agents.planner import PlannerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent
from agents.fixer import FixerAgent
from agents.analyzer import AnalyzerAgent
from agents.saboteur import SaboteurAgent
from agents.enforcer import EnforcerAgent
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
        self.analyzer = AnalyzerAgent()
        self.saboteur = SaboteurAgent()
        self.enforcer = EnforcerAgent()
        self.active_projects: Dict[str, ProjectState] = {}
        self.active_challenges: Dict[str, Dict[str, Any]] = {}
    
    async def create_project(self, 
                           project_id: str, 
                           project_name: str, 
                           goal: str, 
                           tech_stack: List[str] = None,
                           style_guide: str = None,
                           spec_constraints: str = None,
                           websocket_callback = None) -> ProjectState:
        """
        Create a new project using all agents
        """
        # Initialize project state
        project_state = ProjectState(project_id, project_name, goal, tech_stack)
        project_state.metadata = {
            "style_guide": style_guide,
            "spec_constraints": spec_constraints
        }
        self.active_projects[project_id] = project_state
        
        # Save initial state
        await file_manager.save_project_state(project_id, project_state.to_dict())
        
        # Callback for progress updates
        def update_progress(step: str, message: str, data: Dict[str, Any] = None):
            project_state.add_log("progress", message, data)
            if websocket_callback:
                import asyncio
                # Use call_soon_threadsafe or create_task if we were in an async loop
                # but update_progress is called from sync agents sometimes? 
                # Actually agents are often async in this system.
                # Let's check orchestrator again.
                asyncio.create_task(websocket_callback({
                    "type": "progress",
                    "step": step,
                    "message": message,
                    "data": data or {}
                }))
                # Also save state to disk
                asyncio.create_task(file_manager.save_project_state(project_id, project_state.to_dict()))

    async def _run_with_timeout(self, coro, timeout: int, task_name: str):
        """Run a coroutine with a timeout"""
        import asyncio
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Task '{task_name}' timed out after {timeout}s")
            raise

        
        try:
            # Step 1: Planning
            project_state.update_status(ProjectStatus.PLANNING)
            update_progress("planning", "Creating project plan...")
            
            # Pass tech stack if provided in project_data (we need to update Main as well)
            tech_stack = getattr(project_state, 'tech_stack', None)
            
            # Critical step: Planning (Retry but don't skip if fails totally)
            try:
                plan = await self._run_with_timeout(
                    self.planner.create_plan(goal, project_name, tech_stack), 
                    timeout=60, 
                    task_name="Planning"
                )
            except asyncio.TimeoutError:
                raise Exception("Planning stage timed out")
                
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
                
                # Generate code (Critical per file)
                try:
                    code = await self._run_with_timeout(
                        self.developer.write_file(file_spec, plan),
                        timeout=120,
                        task_name=f"Coding {file_path}"
                    )
                except asyncio.TimeoutError:
                    update_progress("error", f"Timeout generating {file_path}. Skipping file.")
                    project_state.add_error(f"Timeout generating {file_path}")
                    continue

                # Step 2.1: Enforcement (Phase 3) - Skip on timeout
                try:
                    review = await self._run_with_timeout(
                        self.enforcer.enforce(
                            code, 
                            file_path, 
                            project_state.metadata.get("style_guide"), 
                            project_state.metadata.get("spec_constraints")
                        ),
                        timeout=30,
                        task_name=f"Enforcing {file_path}"
                    )
                    
                    if not review.get("compliant", True):
                        update_progress("enforcement", f"Style Violation in {file_path}", {"violations": review.get("violations")})
                        # Re-write with feedback (Best effort)
                        try:
                            code = await self._run_with_timeout(
                                self.developer.write_file(
                                    file_spec, 
                                    {**plan, "feedback": review.get('feedback'), "violations": json.dumps(review.get('violations'))}
                                ),
                                timeout=60,
                                task_name=f"Fixing violations {file_path}"
                            )
                        except asyncio.TimeoutError:
                             update_progress("warning", f"Timeout fixing violations for {file_path}. Using original code.")
                except asyncio.TimeoutError:
                    update_progress("warning", f"Enforcement timed out for {file_path}. Skipping checks.")
                
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
                try:
                    test_code = await self._run_with_timeout(
                        self.tester.create_tests(code, file_path, {"language": file_lang}),
                        timeout=60,
                        task_name=f"Creating tests {file_path}"
                    )
                except asyncio.TimeoutError:
                    update_progress("warning", f"Timeout creating tests for {file_path}. Skipping tests.")
                    continue
                
                # File naming convention for tests
                ext = file_path.split('.')[-1]
                test_file_name = f"test_{file_path.replace('.' + ext, '')}.{ext}" if file_lang == 'python' else f"{file_path.replace('.' + ext, '')}.test.{ext}"
                
                await file_manager.save_file(project_id, test_file_name, test_code)
                
                # Execute tests
                workspace_path = file_manager.get_project_dir(project_id)
                test_result = await self._run_with_timeout(
                    self.tester.run_test_file(test_file_name, workspace_path, file_lang),
                    timeout=30,
                    task_name=f"Running tests {file_path}"
                )
                
                if test_result["success"]:
                    update_progress("testing", f"✅ Tests passed for {file_path}")
                    project_state.add_log("test_success", f"Tests passed for {file_path}")
                else:
                    # FIX LOOP (Maximum 2 attempts for now)
                    for attempt in range(2):
                        update_progress("fixing", f"🔧 Tests failed for {file_path}. Attempting fix {attempt+1}/2...")
                        project_state.add_log("test_failure", f"Tests failed for {file_path}", {"error": test_result["error"]})
                        
                        try:
                            # Fix code
                            fixed_code = await self._run_with_timeout(
                                self.fixer.fix_code(code, test_result["error"], file_path, file_lang),
                                timeout=60,
                                task_name=f"Fixing {file_path}"
                            )
                            await file_manager.save_file(project_id, file_path, fixed_code)
                            code = fixed_code # Update for next attempt if needed
                            
                            # Re-run tests
                            test_result = await self._run_with_timeout(
                                self.tester.run_test_file(test_file_name, workspace_path, file_lang),
                                timeout=30,
                                task_name=f"Re-running tests {file_path}"
                            )
                            if test_result["success"]:
                                update_progress("fixing", f"✅ Fixed {file_path} successfully!")
                                break
                        except asyncio.TimeoutError:
                            update_progress("warning", f"Timeout trying to fix {file_path}. Skipping fix.")
                            break
                    
                    if not test_result.get("success", False):
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
    
    async def analyze_project(self, project_id: str) -> Dict[str, Any]:
        """
        Analyze an existing project's codebase
        """
        project_state = await self.get_project_state(project_id)
        if not project_state:
            # Simple metadata for analysis if not even on disk
            project_state = ProjectState(project_id, project_id, "Existing Project")
            self.active_projects[project_id] = project_state

        # Collect all files for analysis
        project_dir = file_manager.get_project_dir(project_id)
        files_content = {}
        
        # Walk through the project directory
        import os
        for root, dirs, files in os.walk(project_dir):
            # Skip hidden dirs and common bulky dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.html', '.css', '.md')):
                    file_path = os.path.relpath(os.path.join(root, file), project_dir)
                    try:
                        content = await file_manager.read_file(project_id, file_path)
                        files_content[file_path] = content
                    except Exception as e:
                        logger.warning(f"Could not read {file_path} for analysis: {e}")

        if not files_content:
            return {"error": "No source files found to analyze"}

        # Run analysis with timeout
        try:
            analysis = await self._run_with_timeout(
                self.analyzer.analyze_codebase(files_content, {
                    "project_name": project_state.project_name,
                    "project_goal": project_state.goal
                }),
                timeout=120,
                task_name="Analyzing Codebase"
            )
        except asyncio.TimeoutError:
            return {"error": "Analysis timed out. Codebase might be too large."}
        
        project_state.add_log("analysis_complete", "Codebase analysis finished", {"debt_items": len(analysis.get("technical_debt", []))})
        return analysis

    async def start_dojo_challenge(self, project_id: str) -> Dict[str, Any]:
        """
        Start a debugging challenge by sabotaging a file
        """
        project_state = await self.get_project_state(project_id)
        if not project_state:
            raise ValueError(f"Project {project_id} not found")

        # Pick a suitable file (source file, not test)
        source_files = [f for f in project_state.files if not f.startswith('test_') and f.endswith(('.py', '.js', '.go'))]
        if not source_files:
            raise ValueError("No suitable source files for Dojo challenge")
        
        import random
        target_file = random.choice(source_files)
        
        # Save original content for verification
        original_code = await file_manager.read_file(project_id, target_file)
        
        # Sabotage!
        ext = target_file.split('.')[-1]
        lang = "python" if ext == "py" else "javascript" if ext in ["js", "ts"] else "go"
        
        try:
            sabotage_result = await self._run_with_timeout(
                self.saboteur.sabotage_file(original_code, target_file, lang),
                timeout=60,
                task_name="Dojo Sabotage"
            )
        except asyncio.TimeoutError:
            raise Exception("Sabotage agent timed out. Mission aborted.")
        
        sabotaged_code = sabotage_result.get("sabotaged_code", original_code)
        mission_hint = sabotage_result.get("mission_hint", "Systems failing. No diagnostic data.")
        bug_intel = sabotage_result.get("intel", "Logic breach in core modules.")
        
        # Save sabotaged code
        await file_manager.save_file(project_id, target_file, sabotaged_code)
        
        # Store challenge state
        import time
        challenge_id = f"dojo_{int(time.time())}"
        self.active_challenges[project_id] = {
            "id": challenge_id,
            "file": target_file,
            "start_time": time.time(),
            "original_code": original_code,
            "hint": mission_hint,
            "intel": bug_intel
        }
        
        project_state.add_log("dojo_challenge", f"Dojo Challenge Started: Sabotaged {target_file}", {"challenge_id": challenge_id, "intel": bug_intel})
        
        return {
            "challenge_id": challenge_id,
            "message": f"A subtle logic bug has been injected into the system.\n\nERROR INTEL: {bug_intel}\n\nMISSION HINT: {mission_hint}"
        }

    async def verify_dojo_fix(self, project_id: str) -> Dict[str, Any]:
        """
        Verify if the user has fixed the sabotaged file
        """
        project_state = await self.get_project_state(project_id)
        challenge = self.active_challenges.get(project_id)
        if not challenge:
            raise ValueError("No active challenge for this project")
        
        target_file = challenge["file"]
        current_code = await file_manager.read_file(project_id, target_file)
        
        # 1. Check if matches original exactly
        if current_code.strip() == challenge["original_code"].strip():
            duration = int(time.time() - challenge["start_time"])
            del self.active_challenges[project_id]
            return {
                "success": True,
                "message": f"EXCELLENT. System restored in {duration} seconds.",
                "duration": duration
            }

        # 2. Run tests as fallback verification
        workspace_path = file_manager.get_project_dir(project_id)
        ext = target_file.split('.')[-1]
        lang = "python" if ext == "py" else "javascript" if ext in ["js", "ts"] else "go"
        
        # Guess test file name
        test_file = f"test_{target_file}" if lang == 'python' else target_file.replace('.'+ext, '.test.'+ext)
        
        test_result = await self.tester.run_test_file(test_file, workspace_path, lang)
        
        if test_result["success"]:
            duration = int(time.time() - challenge["start_time"])
            del self.active_challenges[project_id]
            return {
                "success": True,
                "message": f"CRITICAL_FIX_VERIFIED. Tests passed in {duration} seconds.",
                "duration": duration
            }
        
        return {
            "success": False,
            "error": test_result.get("error", "Tests are still failing.")
        }

    async def get_project_state(self, project_id: str) -> Optional[ProjectState]:
        """Get current project state (loads from disk if missing from memory)"""
        if project_id in self.active_projects:
            return self.active_projects[project_id]
            
        # Try to load from disk
        state_dict = await file_manager.load_project_state(project_id)
        if state_dict:
            try:
                state = ProjectState.from_dict(state_dict)
                self.active_projects[project_id] = state
                return state
            except Exception as e:
                logger.error(f"Failed to rehydrate project {project_id}: {e}")
        
        # State Recovery: If metadata is missing but folder exists, reconstruct state
        project_dir = file_manager.workspace_path / project_id
        if project_dir.exists() and project_dir.is_dir():
            logger.warning(f"Project {project_id} exists but missing metadata. Attempting recovery.")
            try:
                # Create a recovered state
                # We don't know the original name/goal/stack, so we use placeholders
                state = ProjectState(
                    project_id=project_id,
                    project_name=f"Recovered Project {project_id}",
                    goal="Recovered from existing files",
                    tech_stack=["unknown"] 
                )
                state.status = ProjectStatus.COMPLETED # Assume completed if it exists
                
                # Scan for files
                files = file_manager.get_project_files(project_id)
                project_state_files = []
                for f in files:
                    if not f.endswith('.metadata.json'):
                        project_state_files.append(f)
                
                state.files = project_state_files
                state.add_log("recovery", "Project state recovered from disk files")
                
                # Save restored state
                await file_manager.save_project_state(project_id, state.to_dict())
                
                self.active_projects[project_id] = state
                return state
                
            except Exception as e:
                 logger.error(f"Failed to recover project {project_id}: {e}")

        return None