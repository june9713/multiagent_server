"""
FastAPI MCP Server - Main entry point
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from dotenv import load_dotenv
import uvicorn

from core.agent_loader import AgentLoader
from core.history_manager import HistoryManager
from core.context_manager import ContextManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MCP Multi-Agent Server",
    description="Multi-Agent System based on Model Context Protocol",
    version="1.0.0"
)

# Global instances
agent_loader: Optional[AgentLoader] = None
history_manager: Optional[HistoryManager] = None
context_manager: Optional[ContextManager] = None


class AgentRequest(BaseModel):
    """Request model for agent invocation"""
    agent_id: str
    message: str
    session_id: Optional[str] = None
    context_package: Optional[Dict] = None


class AgentResponse(BaseModel):
    """Response model for agent invocation"""
    agent_id: str
    agent_name: str
    session_id: str
    response: str
    status: str = "success"


@app.on_event("startup")
async def startup_event():
    """Initialize agents and managers on startup"""
    global agent_loader, history_manager, context_manager
    
    print("🚀 Starting MCP Multi-Agent Server...")
    
    # Get paths
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "agentconfig.json"
    db_path = base_dir / "data" / "history.db"
    work_docs_dir = base_dir / "data" / "work_docs"
    
    # Ensure directories exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    work_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Get API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("⚠️  Warning: GEMINI_API_KEY not set in environment")
    
    # Initialize managers
    history_manager = HistoryManager(db_path)
    context_manager = ContextManager(work_docs_dir)
    
    # Load agents
    agent_loader = AgentLoader(config_path, gemini_api_key, work_docs_dir)
    try:
        agents = agent_loader.load_agents()
        print(f"✅ Loaded {len(agents)} agents successfully")
    except Exception as e:
        print(f"❌ Failed to load agents: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MCP Multi-Agent Server",
        "version": "1.0.0",
        "status": "running",
        "agents_loaded": len(agent_loader.agents) if agent_loader else 0
    }


@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents"""
    if not agent_loader:
        raise HTTPException(status_code=500, detail="Agent loader not initialized")
    
    return {
        "agents": agent_loader.list_agents(),
        "total": len(agent_loader.agents)
    }


@app.post("/api/v1/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """Invoke an agent with a message"""
    if not agent_loader:
        raise HTTPException(status_code=500, detail="Agent loader not initialized")
    
    # Get agent
    agent = agent_loader.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent_id}' not found"
        )
    
    # Generate session ID if not provided
    session_id = request.session_id or f"session-{os.urandom(8).hex()}"
    
    try:
        # Process message
        response = await agent.process(
            user_message=request.message,
            session_id=session_id,
            context_package=request.context_package
        )
        
        # Save to history
        if history_manager:
            history_manager.save_message(session_id, request.agent_id, "user", request.message)
            history_manager.save_message(session_id, request.agent_id, "model", response)
        
        return AgentResponse(
            agent_id=request.agent_id,
            agent_name=agent.agent_name,
            session_id=session_id,
            response=response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/api/v1/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent's current status from work_docs"""
    if not context_manager:
        raise HTTPException(status_code=500, detail="Context manager not initialized")
    
    try:
        context = context_manager.load_agent_context(agent_id)
        return {
            "agent_id": agent_id,
            "context": context
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading agent status: {str(e)}"
        )


@app.get("/api/v1/sessions")
async def list_sessions(agent_id: Optional[str] = None):
    """List conversation sessions"""
    if not history_manager:
        raise HTTPException(status_code=500, detail="History manager not initialized")
    
    sessions = history_manager.list_sessions(agent_id)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@app.get("/api/v1/session/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 50):
    """Get conversation history for a session"""
    if not history_manager:
        raise HTTPException(status_code=500, detail="History manager not initialized")
    
    history = history_manager.load_history(session_id, limit)
    session_info = history_manager.get_session_info(session_id)
    
    return {
        "session_id": session_id,
        "session_info": session_info,
        "history": history,
        "message_count": len(history)
    }


def main():
    """Run the server"""
    host = os.getenv("MCP_HOST", "localhost")
    port = int(os.getenv("MCP_PORT", 8000))
    
    print(f"\n🌐 Starting server at http://{host}:{port}")
    print(f"📚 API docs at http://{host}:{port}/docs\n")
    
    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        reload=True
    )


if __name__ == "__main__":
    main()
