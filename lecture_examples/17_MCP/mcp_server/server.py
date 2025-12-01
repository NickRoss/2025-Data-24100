"""MCP Server implementation for Basketball API using FastMCP.

This module provides an MCP server that exposes basketball data tools
for AI assistants to interact with the basketball database.
"""

import logging

# Import the mcp instance with tools already registered
from tools import mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Run with HTTP/SSE transport
    logger.info("Starting Basketball API MCP Server (HTTP/SSE mode)")
    mcp.run(transport="sse", host="0.0.0.0", port=3000)
