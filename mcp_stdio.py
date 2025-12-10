#!/usr/bin/env python3
"""MCP stdio wrapper for Windsurf integration.

This script acts as a bridge between Windsurf's stdio-based MCP protocol
and AgentParty's HTTP endpoint.
"""

import asyncio
import json
import sys

import httpx


async def main():
    """Main stdio loop for MCP communication."""
    # Change this to your deployed server URL
    # Examples:
    # - http://agentparty.yourcompany.com/mcp
    # - https://your-server.azurewebsites.net/mcp
    # - http://your-vm-ip:8000/mcp
    base_url = "http://localhost:8000/mcp"  # Replace with deployed URL
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Read from stdin line by line
        for line in sys.stdin:
            try:
                # Parse JSON-RPC request from Windsurf
                request = json.loads(line.strip())
                
                # Forward to AgentParty HTTP endpoint
                response = await client.post(
                    base_url,
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                
                # Get response
                result = response.json()
                
                # Write response to stdout (for Windsurf)
                sys.stdout.write(json.dumps(result) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
