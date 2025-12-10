"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    settings = get_settings()
    logger.info(f"Starting AgentParty MCP Server v{settings.mcp_server_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize services
    from src.session.manager import get_session_manager
    from src.vectordb.client import get_qdrant_manager
    from src.agents.registry import get_agent_registry
    
    # Test connections
    try:
        session_mgr = await get_session_manager()
        logger.info("✓ Redis connection established")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
    
    try:
        qdrant_mgr = await get_qdrant_manager()
        if await qdrant_mgr.health_check():
            logger.info("✓ Qdrant connection established")
        else:
            logger.error("✗ Qdrant health check failed")
    except Exception as e:
        logger.error(f"✗ Qdrant connection failed: {e}")
    
    # Load agents
    agent_registry = get_agent_registry()
    logger.info(f"✓ Loaded {len(agent_registry.list())} agents")
    
    # Start agent hot-reload watcher
    from src.agents.watcher import start_agent_watcher
    start_agent_watcher(settings.agents_dir)
    logger.info("✓ Agent hot-reload watcher enabled")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down AgentParty MCP Server")
    
    # Stop agent watcher
    from src.agents.watcher import stop_agent_watcher
    stop_agent_watcher()


# Create FastAPI application
app = FastAPI(
    title="AgentParty MCP Server",
    description="Multi-agent LLM workflow platform with Model Context Protocol support",
    version=get_settings().mcp_server_version,
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "agentparty-mcp",
            "version": get_settings().mcp_server_version,
        }
    )


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint with service information."""
    settings = get_settings()
    return JSONResponse(
        content={
            "service": "AgentParty MCP Server",
            "version": settings.mcp_server_version,
            "environment": settings.environment,
            "mcp_endpoint": "/mcp",
            "health_endpoint": "/health",
        }
    )


# MCP server endpoints (Streamable HTTP with SSE)
@app.post("/mcp")
@app.get("/mcp")
async def mcp_endpoint(request: Request):
    """MCP Streamable HTTP endpoint with SSE support.
    
    Supports:
    - POST: Client-to-server JSON-RPC messages
    - GET: SSE stream for server-to-client messages
    """
    from src.mcp.sse_transport import get_mcp_transport
    
    transport = get_mcp_transport()
    
    # Handle GET for SSE stream
    if request.method == "GET":
        return await transport.handle_get(request)
    
    # Handle POST for JSON-RPC messages
    body = await request.json()
    return await transport.handle_post(request, body)


# API routes for direct access
@app.get("/api/agents")
async def list_agents() -> dict:
    """List all available agents."""
    from src.agents.registry import get_agent_registry
    
    registry = get_agent_registry()
    agents = registry.list()
    
    return {"agents": agents, "count": len(agents)}


@app.get("/api/workflows")
async def list_workflows() -> dict:
    """List all available workflows."""
    from src.workflows.loader import list_available_workflows
    
    workflows = list_available_workflows()
    return {"workflows": workflows, "count": len(workflows)}


@app.get("/api/jobs")
async def list_jobs(assigned_to: str = None) -> dict:
    """List all available jobs."""
    from src.jobs.loader import list_available_jobs
    
    jobs = list_available_jobs(assigned_to=assigned_to)
    return {"jobs": jobs, "count": len(jobs)}
