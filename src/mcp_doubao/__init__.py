"""MCP Doubao: A Model Context Protocol server for Doubao image generation."""

__version__ = "0.1.0"
__author__ = "MCP Doubao Team"
__description__ = "MCP server for Doubao AI image generation using Ark SDK"

from .server import app, run_stdio
from .tools import GENERATE_IMAGES_TOOL, handle_generate_images, COMPRESS_IMAGES_TOOL, handle_compress_images
from .doubao_client import DoubaoClient
from .downloader import ImageDownloader
from .types import GenerateImagesRequest, ImageItem, GenerateImagesResponse

__all__ = [
    # Server components
    "app",
    "run_stdio",

    # Tool components
    "GENERATE_IMAGES_TOOL",
    "handle_generate_images",
    "COMPRESS_IMAGES_TOOL",
    "handle_compress_images",

    # Client and downloader
    "DoubaoClient",
    "ImageDownloader",

    # Types
    "GenerateImagesRequest",
    "ImageItem",
    "GenerateImagesResponse",
]