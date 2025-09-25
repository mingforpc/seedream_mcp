"""Doubao Ark SDK client for image generation."""

from typing import List
import logging
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images import SequentialImageGenerationOptions

from .config import BASE_URL, MODEL_ID, ARK_API_KEY
from .types import ImageItem


logger = logging.getLogger(__name__)


class DoubaoClient:
    """Client for interacting with Doubao Ark image generation API."""

    def __init__(self):
        """Initialize the Doubao client."""
        if not ARK_API_KEY or ARK_API_KEY == "REPLACE_WITH_YOUR_KEY":
            raise ValueError(
                "Please set the ARK_API_KEY environment variable. "
                "You can get your API key from https://console.volcengine.com/ark"
            )

        self.client = Ark(
            base_url=BASE_URL,
            api_key=ARK_API_KEY
        )

    def generate_images(
        self,
        prompt: str,
        count: int,
        size: str,
        watermark: bool,
        images: List[str] = None,
        sequential_mode: str = "auto",
        max_images: int = None
    ) -> List[ImageItem]:
        """
        Generate images using Doubao Ark API.

        Args:
            prompt: Text description for image generation
            count: Number of images to generate (1-3)
            size: Image size specification
            watermark: Whether to add watermark
            images: List of base64 encoded reference images (optional)
            sequential_mode: Sequential generation mode ("auto", "true", "false")
            max_images: Max images for sequential generation (overrides count if provided)

        Returns:
            List of ImageItem objects containing URLs and sizes

        Raises:
            Exception: If API call fails or returns unexpected format
        """
        try:
            # Use max_images if provided, otherwise use count
            target_count = max_images if max_images is not None else count

            logger.info(f"Generating {target_count} images with prompt: {prompt[:50]}...")
            if images:
                logger.info(f"Using {len(images)} reference images")

            # Prepare request parameters
            request_params = {
                "model": MODEL_ID,
                "prompt": prompt,
                "size": size,
                "sequential_image_generation": sequential_mode,
                "sequential_image_generation_options": SequentialImageGenerationOptions(
                    max_images=target_count
                ),
                "response_format": "url",
                "watermark": watermark
            }

            # Add reference images if provided
            if images:
                request_params["image"] = images

            logger.debug(f"Request parameters: {request_params}")

            # Call Doubao Ark API
            response = self.client.images.generate(**request_params)

            logger.debug(f"API response: {response}")

            # Parse response
            if not hasattr(response, 'data') or not response.data:
                raise Exception("API response missing data field or data is empty")

            images = []
            for item in response.data:
                if not hasattr(item, 'url'):
                    raise Exception(f"Response item missing url field: {item}")

                # Extract size from response item or use requested size as fallback
                item_size = getattr(item, 'size', size)

                images.append(ImageItem(
                    url=item.url,
                    size=item_size
                ))

            logger.info(f"Successfully generated {len(images)} images")
            return images

        except Exception as e:
            logger.error(f"Error generating images: {str(e)}")
            raise Exception(f"Failed to generate images: {str(e)}")