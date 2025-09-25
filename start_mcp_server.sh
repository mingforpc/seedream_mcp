#!/bin/bash

# MCP Doubao Server Startup Script
# This script ensures proper environment setup for Claude Code

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Export environment variables
export PYTHONPATH="$PROJECT_DIR/src"

# Start the server using the project's virtual environment
exec "$PROJECT_DIR/.venv/bin/python" -m mcp_doubao.server