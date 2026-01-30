"""
Pydantic models for API schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    goal: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Project description / goal for the autonomous coding partner",
    )
    project_name: str = Field(default="New Project", min_length=1)
    tech_stack: Optional[List[str]] = Field(default=["python"])
    requirements: Optional[List[str]] = Field(default=[])
    style_guide: Optional[str] = Field(default=None, description="Custom style guide or rules")
    spec_constraints: Optional[str] = Field(default=None, description="Strict architectural constraints")

class ProjectResponse(BaseModel):
    """Schema for project response"""
    project_id: str
    project_name: str
    goal: str
    status: str  # planning, coding, testing, completed, failed
    created_at: datetime
    tasks: List[str] = []
    files_created: List[str] = []
    error: Optional[str] = None

class AgentTask(BaseModel):
    """Schema for agent task"""
    agent_type: str  # planner, developer, tester, fixer
    task: str
    status: str  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)

class CodeFile(BaseModel):
    """Schema for code file"""
    path: str
    content: str
    language: str
    status: str = "generated"  # generated, tested, fixed

class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str  # progress, error, file_created, task_completed
    project_id: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)