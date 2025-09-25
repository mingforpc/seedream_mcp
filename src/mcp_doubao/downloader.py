"""Image download functionality for MCP Doubao."""

import os
import logging
from typing import List, Tuple
from urllib.parse import urlparse
import httpx
from pathlib import Path

from .types import ImageItem


logger = logging.getLogger(__name__)


class ImageDownloader:
    """Handles downloading images from URLs to local filesystem."""

    def __init__(self):
        """Initialize the image downloader."""
        self.client = httpx.Client(timeout=30.0)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.client.close()

    def _get_filename_from_url(self, url: str, index: int, output_dir: Path) -> str:
        """
        Generate a unique filename from URL and index, avoiding overwriting existing files.

        Args:
            url: Image URL
            index: Image index for unique naming
            output_dir: Output directory to check for existing files

        Returns:
            Generated unique filename
        """
        parsed_url = urlparse(url)
        path = parsed_url.path

        # Try to extract extension from URL path
        extension = "jpeg"  # default
        if path and '.' in path:
            ext = path.split('.')[-1].lower()
            # Validate common image extensions
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                extension = ext

        # Generate base filename
        base_filename = f"image_{index + 1:03d}"
        filename = f"{base_filename}.{extension}"

        # Check if file exists and generate unique name
        counter = 1
        while (output_dir / filename).exists():
            filename = f"{base_filename}_{counter}.{extension}"
            counter += 1

        return filename

    def _ensure_directory_exists(self, output_dir: str) -> Path:
        """
        Ensure the output directory exists.

        Args:
            output_dir: Directory path

        Returns:
            Path object for the directory

        Raises:
            OSError: If directory cannot be created
        """
        path = Path(output_dir).resolve()

        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory ready: {path}")
            return path
        except OSError as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise OSError(f"Cannot create output directory {path}: {e}")

    def download_image(self, url: str, filepath: Path) -> bool:
        """
        Download a single image from URL to filepath.

        Args:
            url: Image URL to download
            filepath: Local file path to save to

        Returns:
            True if download successful, False otherwise
        """
        try:
            logger.info(f"Downloading image from: {url}")

            response = self.client.get(url)
            response.raise_for_status()

            # Check if response contains image data
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL may not be an image: content-type={content_type}")

            # Write image data to file
            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Successfully downloaded image to: {filepath}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"HTTP error downloading {url}: {e}")
            return False
        except OSError as e:
            logger.error(f"File system error saving to {filepath}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return False

    def download_images(
        self,
        images: List[ImageItem],
        output_dir: str = "."
    ) -> List[Tuple[ImageItem, str, bool]]:
        """
        Download multiple images to specified directory.

        Args:
            images: List of ImageItem objects to download
            output_dir: Directory to save images (default: current directory)

        Returns:
            List of tuples (ImageItem, local_filepath, success_status)
        """
        results = []

        try:
            # Ensure output directory exists
            dir_path = self._ensure_directory_exists(output_dir)

            logger.info(f"Downloading {len(images)} images to: {dir_path}")

            for index, image in enumerate(images):
                # Generate unique filename
                filename = self._get_filename_from_url(image.url, index, dir_path)
                filepath = dir_path / filename

                # Download image
                success = self.download_image(image.url, filepath)

                # Record result
                results.append((image, str(filepath), success))

                if success:
                    logger.info(f"Image {index + 1}/{len(images)} downloaded successfully")
                else:
                    logger.error(f"Image {index + 1}/{len(images)} download failed")

            successful_count = sum(1 for _, _, success in results if success)
            logger.info(f"Download complete: {successful_count}/{len(images)} successful")

            return results

        except Exception as e:
            logger.error(f"Error during batch download: {e}")
            # Return partial results if any downloads were attempted
            return results