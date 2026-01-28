"""
Main FastAPI application
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import aiofiles

from models.schemas import ProjectCreate, ProjectResponse
from services.file_manager import file_manager
from agents.orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

# Agent orchestrator
orchestrator = AgentOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    logger.info("🚀 Starting Autonomous Coding Partner Backend")
    logger.info(f"Workspace: {os.path.abspath('./workspace')}")
    yield
    # Shutdown
    logger.info("🛑 Shutting down")

# Create FastAPI app
app = FastAPI(
    title="Autonomous Coding Partner API",
    description="AI-powered code generation system using Groq",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def send_websocket_message(project_id: str, message_type: str, data: Dict[str, Any]):
    """Send message to all WebSocket connections for a project"""
    if project_id in active_connections:
        message = {
            "type": message_type,
            "project_id": project_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for connection in active_connections[project_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")

async def create_project_task(project_id: str, project_data: ProjectCreate):
    """Background task to create a project"""
    try:
        # WebSocket callback
        async def ws_callback(message: Dict[str, Any]):
            await send_websocket_message(project_id, message["type"], {
                "step": message.get("step"),
                "message": message.get("message"),
                **message.get("data", {})
            })
        
        # Create project using orchestrator
        project_state = await orchestrator.create_project(
            project_id=project_id,
            project_name=project_data.project_name,
            goal=project_data.goal,
            websocket_callback=ws_callback
        )
        
        logger.info(f"✅ Project {project_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error creating project {project_id}: {e}")
        await send_websocket_message(project_id, "error", {
            "message": f"Project failed: {str(e)}"
        })

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Autonomous Coding Partner API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, background_tasks: BackgroundTasks):
    """Create a new project"""
    project_id = str(uuid.uuid4())[:8]  # Short ID
    
    # Start background task
    background_tasks.add_task(create_project_task, project_id, project_data)
    
    return ProjectResponse(
        project_id=project_id,
        project_name=project_data.project_name,
        goal=project_data.goal,
        status="pending",
        created_at=datetime.now(),
        tasks=[],
        files_created=[]
    )

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project status"""
    project_state = orchestrator.get_project_state(project_id)
    if not project_state:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project_state.to_dict()

@app.get("/api/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get list of files in project"""
    files = file_manager.get_project_files(project_id)
    return {"project_id": project_id, "files": files}

@app.get("/api/projects/{project_id}/files/{file_path:path}")
async def get_file_content(project_id: str, file_path: str):
    """Get file content"""
    content = await file_manager.read_file(project_id, file_path)
    if not content:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "project_id": project_id,
        "path": file_path,
        "content": content,
        "size": len(content)
    }

@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket for real-time updates"""
    await websocket.accept()
    
    # Add connection to active connections
    if project_id not in active_connections:
        active_connections[project_id] = []
    active_connections[project_id].append(websocket)
    
    try:
        # Send initial project state if exists
        project_state = orchestrator.get_project_state(project_id)
        if project_state:
            await websocket.send_json({
                "type": "state",
                "project_id": project_id,
                "data": project_state.to_dict()
            })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove connection
        if project_id in active_connections:
            active_connections[project_id].remove(websocket)
            if not active_connections[project_id]:
                del active_connections[project_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )