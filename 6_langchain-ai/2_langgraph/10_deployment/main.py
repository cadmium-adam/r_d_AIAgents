from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage, AIMessage
from agent import create_agent_graph
import uuid

# Pydantic models for request/response
class HealthResponse(BaseModel):
    status: str
    message: str

class AgentRequest(BaseModel):
    message: str
    session_id: str = None

class AgentResponse(BaseModel):
    response: str
    session_id: str

# In-memory session storage (use Redis or database in production)
sessions: Dict[str, list] = {}

# Global agent graph instance
agent_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global agent_graph
    # Startup
    print("Initializing agent graph with MCP tools...")
    agent_graph = await create_agent_graph()
    print("Agent graph initialized successfully!")
    yield
    # Shutdown (cleanup if needed)
    print("Shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="FastAPI with LangGraph Agent",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="FastAPI server is running successfully"
    )

@app.post("/agent", response_model=AgentResponse)
async def call_agent(request: AgentRequest):
    """Endpoint that calls the LangGraph agent"""
    global agent_graph

    if agent_graph is None:
        raise HTTPException(status_code=503, detail="Agent not initialized yet")

    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Get or create session messages
        if session_id not in sessions:
            sessions[session_id] = []

        # Add user message to session
        user_message = HumanMessage(content=request.message)
        sessions[session_id].append(user_message)

        # Create initial state
        initial_state = {
            "messages": sessions[session_id],
        }

        # Run the agent asynchronously
        result = await agent_graph.ainvoke(initial_state)

        # Update session with new messages
        sessions[session_id] = result["messages"]

        # Get the last AI message
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        response_content = ai_messages[-1].content if ai_messages else "No response generated"

        return AgentResponse(
            response=response_content,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = []
    for msg in sessions[session_id]:
        messages.append({
            "type": "human" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content
        })
    
    return {"session_id": session_id, "messages": messages}

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)