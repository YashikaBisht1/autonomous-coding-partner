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
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectState:
    """Manages project state"""
    
    def __init__(self, project_id: str, project_name: str, goal: str):
        self.project_id = project_id
        self.project_name = project_name
        self.goal = goal
        self.status: ProjectStatus = ProjectStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.tasks: List[Dict[str, Any]] = []
        self.files: List[str] = []
        self.errors: List[str] = []
        self.logs: List[Dict[str, Any]] = []
    
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
            "logs": self.logs
        }