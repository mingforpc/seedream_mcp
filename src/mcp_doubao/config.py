"""Configuration constants for MCP Doubao integration."""

import os

# Doubao Ark API Configuration
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID = "doubao-seedream-4-0-250828"

# API Key for Doubao Ark - loaded from environment variable
ARK_API_KEY = os.getenv("ARK_API_KEY", "")

# Default parameters
DEFAULT_SIZE = "2K"
MAX_IMAGES = 3

# Available image sizes (for reference)
AVAILABLE_SIZES = [
    "1K",      # 1024x1024
    "2K",      # 2048x2048
    "4K",      # 4096x4096
]