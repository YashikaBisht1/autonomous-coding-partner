import asyncio
import os
import logging
from agents.orchestrator import AgentOrchestrator

# Setup logging to see agent progress
logging.basicConfig(level=logging.INFO)

async def main():
    print("🚀 Starting direct agent test...")
    orchestrator = AgentOrchestrator()
    
    project_id = "test_calc"
    project_name = "Python Calculator"
    goal = "Create a simple Python calculator that can add, subtract, multiply, and divide."
    
    print(f"Generating project: {project_name} ({project_id})...")
    
    try:
        # Run orchestrator
        project_state = await orchestrator.create_project(
            project_id=project_id,
            project_name=project_name,
            goal=goal
        )
        
        print("\n✅ Project Generation Complete!")
        print(f"Status: {project_state.status}")
        print(f"Files created: {project_state.files}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
