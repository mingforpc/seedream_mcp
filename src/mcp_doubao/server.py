"""MCP server for Doubao image generation."""

import logging
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

from .tools import GENERATE_IMAGES_TOOL, handle_generate_images, COMPRESS_IMAGES_TOOL, handle_compress_images


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create MCP server instance
app = Server("mcp-doubao")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [GENERATE_IMAGES_TOOL, COMPRESS_IMAGES_TOOL]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "generate_images":
        return await handle_generate_images(arguments)
    elif name == "compress_images":
        return await handle_compress_images(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server."""
    logger.info("Starting MCP Doubao server...")

    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run_stdio():
    """Run the server with stdio transport (synchronous entry point)."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    run_stdio()