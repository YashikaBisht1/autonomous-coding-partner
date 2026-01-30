"""
Project state management
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enum"""
    PENDING = "pending"
    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    ANALYZING = "analyzing"
    DOJO = "dojo_mode"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectState:
    """Manages project state"""
    
    def __init__(self, project_id: str, project_name: str, goal: str, tech_stack: List[str] = None):
        self.project_id = project_id
        self.project_name = project_name
        self.goal = goal
        self.tech_stack = tech_stack or ["python"]
        self.status: ProjectStatus = ProjectStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.tasks: List[Dict[str, Any]] = []
        self.files: List[str] = []
        self.errors: List[str] = []
        self.logs: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Recreate project state from dictionary"""
        state = cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            goal=data["goal"],
            tech_stack=data.get("tech_stack", ["python"])
        )
        state.status = ProjectStatus(data["status"])
        state.created_at = datetime.fromisoformat(data["created_at"])
        state.updated_at = datetime.fromisoformat(data["updated_at"])
        state.tasks = data.get("tasks", [])
        state.files = data.get("files", [])
        state.errors = data.get("errors", [])
        state.logs = data.get("logs", [])
        state.metadata = data.get("metadata", {})
        return state
    
    def update_status(self, status: ProjectStatus):
        """Update project status"""
        self.status = status
        self.updated_at = datetime.now()
    
    def add_task(self, task: Dict[str, Any]):
        """Add a task to the project"""
        self.tasks.append(task)
    
    def add_file(self, file_path: str):
        """Add a generated file"""
        self.files.append(file_path)
    
    def add_error(self, error: str):
        """Add an error"""
        self.errors.append(error)
    
    def add_log(self, log_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Add a log entry"""
        self.logs.append({
            "type": log_type,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "goal": self.goal,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tasks": self.tasks,
            "files": self.files,
            "errors": self.errors,
            "logs": self.logs,
            "metadata": self.metadata
        }