"""Data types for MCP Doubao image generation."""

from typing import List
from dataclasses import dataclass


@dataclass
class GenerateImagesRequest:
    """Request for generating images."""
    prompt: str
    num_images: int = 1
    size: str = "2K"
    watermark: bool = True

    def __post_init__(self):
        """Validate request parameters."""
        if not self.prompt or not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if not isinstance(self.num_images, int) or self.num_images < 1 or self.num_images > 3:
            raise ValueError("num_images must be an integer between 1 and 3")

        if not isinstance(self.size, str):
            raise ValueError("size must be a string")

        if not isinstance(self.watermark, bool):
            raise ValueError("watermark must be a boolean")


@dataclass
class ImageItem:
    """Single generated image item."""
    url: str
    size: str

    def __post_init__(self):
        """Validate image item."""
        if not self.url or not isinstance(self.url, str):
            raise ValueError("url must be a non-empty string")

        if not self.size or not isinstance(self.size, str):
            raise ValueError("size must be a non-empty string")


@dataclass
class GenerateImagesResponse:
    """Response containing generated images."""
    images: List[ImageItem]
    count: int

    def __post_init__(self):
        """Validate response."""
        if not isinstance(self.images, list):
            raise ValueError("images must be a list")

        if not isinstance(self.count, int) or self.count < 0:
            raise ValueError("count must be a non-negative integer")

        if self.count != len(self.images):
            raise ValueError("count must match the number of images")