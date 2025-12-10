"""MCP Streamable HTTP (SSE) Transport Implementation."""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional
from uuid import uuid4

from fastapi import Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from src.mcp.tools import MCPTools
from src.session.auth import create_session, validate_session

logger = logging.getLogger(__name__)


class MCPSSETransport:
    """MCP Streamable HTTP transport using SSE."""

    def __init__(self):
        """Initialize SSE transport."""
        self.sessions: Dict[str, Any] = {}

    async def handle_post(self, request: Request, body: dict) -> Any:
        """Handle HTTP POST for client-to-server messages.
        
        Args:
            request: FastAPI request
            body: JSON-RPC message
            
        Returns:
            JSON response or SSE stream
        """
        # Extract JSON-RPC fields
        jsonrpc = body.get("jsonrpc", "2.0")
        method = body.get("method")
        params = body.get("params", {})
        msg_id = body.get("id")

        # Handle different message types
        if msg_id is None:
            # Notification (no response expected)
            return {"jsonrpc": "2.0"}, 202
        
        # Request (response expected)
        try:
            result = await self._handle_method(method, params)
            
            # Return JSON response
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def handle_get(self, request: Request) -> EventSourceResponse:
        """Handle HTTP GET for SSE stream.
        
        Args:
            request: FastAPI request
            
        Returns:
            SSE event stream
        """
        async def event_generator() -> AsyncGenerator[dict, None]:
            """Generate SSE events."""
            # Send initial ping
            yield {
                "event": "ping",
                "data": json.dumps({"type": "ping"})
            }
            
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield {
                    "event": "ping",
                    "data": json.dumps({"type": "ping"})
                }
        
        return EventSourceResponse(event_generator())

    async def _handle_method(self, method: str, params: dict) -> Any:
        """Handle JSON-RPC method call.
        
        Args:
            method: Method name
            params: Method parameters
            
        Returns:
            Method result
        """
        # Initialize
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "agentparty",
                    "version": "0.1.0"
                }
            }
        
        # List tools
        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "create_session",
                        "description": "Create a new user session",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"}
                            },
                            "required": ["user_id"]
                        }
                    },
                    {
                        "name": "get_available_jobs",
                        "description": "List available jobs",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "filter": {"type": "string"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "start_job",
                        "description": "Start a job and initialize workflow",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "job_id": {"type": "string"}
                            },
                            "required": ["session_id", "job_id"]
                        }
                    },
                    {
                        "name": "get_current_task",
                        "description": "Get current workflow task",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "submit_work",
                        "description": "Submit completed work",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "work_description": {"type": "string"},
                                "artifacts": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["session_id", "work_description"]
                        }
                    },
                    {
                        "name": "request_review",
                        "description": "Request agent review",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "query_context",
                        "description": "Search codebase context",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "query": {"type": "string"},
                                "limit": {"type": "integer"}
                            },
                            "required": ["session_id", "query"]
                        }
                    },
                    {
                        "name": "get_agent_guidance",
                        "description": "Ask agent for guidance",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"},
                                "agent_id": {"type": "string"},
                                "question": {"type": "string"}
                            },
                            "required": ["session_id", "agent_id", "question"]
                        }
                    },
                    {
                        "name": "get_workflow_status",
                        "description": "Get workflow status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "get_budget_status",
                        "description": "Get budget information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string"}
                            },
                            "required": ["session_id"]
                        }
                    }
                ]
            }
        
        # Call tool
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Route to MCPTools
            if tool_name == "create_session":
                user_id = arguments.get("user_id")
                if not user_id:
                    raise ValueError("user_id required")
                session = await create_session(user_id)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "session_id": session.session_id,
                                "user_id": session.user_id,
                                "expires_at": session.expires_at.isoformat(),
                            })
                        }
                    ]
                }
            
            # All other tools require session
            session_id = arguments.get("session_id")
            if not session_id:
                raise ValueError("session_id required")
            
            session = await validate_session(session_id)
            if not session:
                raise ValueError("Invalid or expired session")
            
            user_id = session.user_id
            
            # Route to appropriate tool
            if tool_name == "get_available_jobs":
                result = await MCPTools.get_available_jobs(
                    user_id=user_id,
                    filter_type=arguments.get("filter"),
                )
            elif tool_name == "start_job":
                result = await MCPTools.start_job(
                    user_id=user_id,
                    job_id=arguments["job_id"],
                    session_id=session_id,
                )
            elif tool_name == "get_current_task":
                result = await MCPTools.get_current_task(user_id=user_id)
            elif tool_name == "submit_work":
                result = await MCPTools.submit_work(
                    user_id=user_id,
                    work_description=arguments["work_description"],
                    artifacts=arguments.get("artifacts"),
                    session_id=session_id,
                )
            elif tool_name == "request_review":
                result = await MCPTools.request_review(
                    user_id=user_id,
                    session_id=session_id,
                    review_context=arguments.get("review_context"),
                )
            elif tool_name == "query_context":
                result = await MCPTools.query_context(
                    user_id=user_id,
                    query=arguments["query"],
                    limit=arguments.get("limit", 5),
                )
            elif tool_name == "get_agent_guidance":
                result = await MCPTools.get_agent_guidance(
                    user_id=user_id,
                    agent_id=arguments["agent_id"],
                    question=arguments["question"],
                    session_id=session_id,
                )
            elif tool_name == "get_workflow_status":
                result = await MCPTools.get_workflow_status(user_id=user_id)
            elif tool_name == "get_budget_status":
                result = await MCPTools.get_budget_status(session_id=session_id)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Return as MCP tool result
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")


# Global transport instance
_transport = MCPSSETransport()


def get_mcp_transport() -> MCPSSETransport:
    """Get MCP transport instance."""
    return _transport
