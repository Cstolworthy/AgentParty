"""MCP server implementation."""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from src.config import get_settings
from src.mcp.tools import MCPTools
from src.session.auth import create_session, validate_session

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """Create and configure MCP server.

    Returns:
        Configured MCP server instance
    """
    settings = get_settings()
    server = Server(settings.mcp_server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="get_available_jobs",
                description="List all jobs available for the current agent to work on",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "filter": {
                            "type": "string",
                            "description": "Optional filter (e.g., 'high-priority')",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="start_job",
                description="Initialize a job and load its workflow",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "job_id": {
                            "type": "string",
                            "description": "ID of the job to start",
                        },
                    },
                    "required": ["session_id", "job_id"],
                },
            ),
            Tool(
                name="get_current_task",
                description="Get the current task based on workflow state",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="submit_work",
                description="Submit completed work for the current step",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "work_description": {
                            "type": "string",
                            "description": "Description of completed work",
                        },
                        "artifacts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File paths or references to created artifacts",
                        },
                    },
                    "required": ["session_id", "work_description"],
                },
            ),
            Tool(
                name="request_review",
                description="Request review/approval from another agent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "review_context": {
                            "type": "string",
                            "description": "Additional context for the reviewer",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="query_context",
                description="Search the codebase vector database for relevant context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "query": {
                            "type": "string",
                            "description": "Natural language search query",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Max results to return",
                            "default": 5,
                        },
                    },
                    "required": ["session_id", "query"],
                },
            ),
            Tool(
                name="get_agent_guidance",
                description="Ask another agent for guidance or consultation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent to consult (e.g., 'manager', 'architect')",
                        },
                        "question": {
                            "type": "string",
                            "description": "Question to ask the agent",
                        },
                    },
                    "required": ["session_id", "agent_id", "question"],
                },
            ),
            Tool(
                name="get_workflow_status",
                description="Get current workflow status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="get_budget_status",
                description="Get budget status for current session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="create_session",
                description="Create a new session for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier",
                        },
                    },
                    "required": ["user_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        import json

        try:
            # Extract session_id and validate
            session_id = arguments.get("session_id")
            user_id = None

            if name == "create_session":
                # Special case: creating a new session
                user_id = arguments.get("user_id")
                if not user_id:
                    return [TextContent(type="text", text=json.dumps({"error": "user_id required"}))]

                session = await create_session(user_id)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "session_id": session.session_id,
                                "user_id": session.user_id,
                                "expires_at": session.expires_at.isoformat(),
                            }
                        ),
                    )
                ]

            # For all other tools, validate session
            if not session_id:
                return [TextContent(type="text", text=json.dumps({"error": "session_id required"}))]

            session = await validate_session(session_id)
            if not session:
                return [TextContent(type="text", text=json.dumps({"error": "Invalid or expired session"}))]

            user_id = session.user_id

            # Route to appropriate tool
            if name == "get_available_jobs":
                result = await MCPTools.get_available_jobs(
                    user_id=user_id,
                    filter_type=arguments.get("filter"),
                )
            elif name == "start_job":
                result = await MCPTools.start_job(
                    user_id=user_id,
                    job_id=arguments["job_id"],
                    session_id=session_id,
                )
            elif name == "get_current_task":
                result = await MCPTools.get_current_task(user_id=user_id)
            elif name == "submit_work":
                result = await MCPTools.submit_work(
                    user_id=user_id,
                    work_description=arguments["work_description"],
                    artifacts=arguments.get("artifacts"),
                    session_id=session_id,
                )
            elif name == "request_review":
                result = await MCPTools.request_review(
                    user_id=user_id,
                    session_id=session_id,
                    review_context=arguments.get("review_context"),
                )
            elif name == "query_context":
                result = await MCPTools.query_context(
                    user_id=user_id,
                    query=arguments["query"],
                    limit=arguments.get("limit", 5),
                )
            elif name == "get_agent_guidance":
                result = await MCPTools.get_agent_guidance(
                    user_id=user_id,
                    agent_id=arguments["agent_id"],
                    question=arguments["question"],
                    session_id=session_id,
                )
            elif name == "get_workflow_status":
                result = await MCPTools.get_workflow_status(user_id=user_id)
            elif name == "get_budget_status":
                result = await MCPTools.get_budget_status(session_id=session_id)
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Tool call error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    logger.info("MCP server configured")
    return server
