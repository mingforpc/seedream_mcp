"""Tests for image compression functionality."""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_doubao.tools import handle_compress_images, _compress_single_image


class TestCompressImages:
    """Test cases for compress_images tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image(self, filename: str, size: tuple = (2048, 2048), format: str = "JPEG") -> Path:
        """Create a test image file."""
        image_path = self.temp_path / filename
        img = Image.new("RGB", size, color="red")
        img.save(image_path, format=format)
        return image_path

    @pytest.mark.asyncio
    async def test_compress_single_image_success(self):
        """Test successful compression of a single image."""
        # Create test image
        input_path = self.create_test_image("test_input.jpg", (2048, 2048))
        output_path = self.temp_path / "test_output.jpg"

        arguments = {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "max_width": 1024,
            "max_height": 1024,
            "quality": 80,
            "format": "JPEG",
            "optimize": True
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "Image compression completed: 1/1 images processed successfully" in result[0].text
        assert output_path.exists()

        # Check that image was resized
        with Image.open(output_path) as img:
            assert img.size == (1024, 1024)

    @pytest.mark.asyncio
    async def test_compress_directory_batch(self):
        """Test batch compression of directory."""
        # Create multiple test images
        self.create_test_image("image1.jpg", (1500, 1500))
        self.create_test_image("image2.png", (2000, 1000))
        self.create_test_image("image3.jpg", (800, 600))

        arguments = {
            "input_path": str(self.temp_path),
            "max_width": 1200,
            "max_height": 800,
            "quality": 85,
            "format": "JPEG"
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "Image compression completed: 3/3 images processed successfully" in result[0].text

        # Check compressed directory exists
        compressed_dir = self.temp_path / "compressed"
        assert compressed_dir.exists()

        # Check all images were compressed (JPEG format saves as .jpeg)
        compressed_files = list(compressed_dir.glob("*_compressed.jpeg"))
        assert len(compressed_files) == 3

    @pytest.mark.asyncio
    async def test_compress_with_aspect_ratio_preservation(self):
        """Test that aspect ratio is preserved during compression."""
        # Create rectangular image
        input_path = self.create_test_image("rect_image.jpg", (3000, 1500))
        output_path = self.temp_path / "rect_output.jpg"

        arguments = {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "max_width": 1200,
            "max_height": 800
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "successfully" in result[0].text

        # Check aspect ratio preserved (should be 1200x600, not 1200x800)
        with Image.open(output_path) as img:
            assert img.size == (1200, 600)  # Maintains 2:1 aspect ratio

    @pytest.mark.asyncio
    async def test_compress_rgba_to_jpeg(self):
        """Test conversion of RGBA image to JPEG."""
        # Create RGBA image with transparency
        input_path = self.temp_path / "rgba_image.png"
        img = Image.new("RGBA", (1000, 1000), color=(255, 0, 0, 128))  # Semi-transparent red
        img.save(input_path, "PNG")

        output_path = self.temp_path / "rgb_output.jpg"

        arguments = {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "format": "JPEG"
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "successfully" in result[0].text

        # Check that output is RGB JPEG
        with Image.open(output_path) as img:
            assert img.mode == "RGB"

    @pytest.mark.asyncio
    async def test_compress_invalid_input_path(self):
        """Test handling of invalid input path."""
        arguments = {
            "input_path": "/nonexistent/path/image.jpg"
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "Error: Invalid parameters" in result[0].text
        assert "Input path does not exist" in result[0].text

    @pytest.mark.asyncio
    async def test_compress_no_output_path_auto_generation(self):
        """Test automatic output path generation."""
        input_path = self.create_test_image("auto_test.jpg")

        arguments = {
            "input_path": str(input_path),
            "max_width": 800,
            "max_height": 600
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "successfully" in result[0].text

        # Check auto-generated output file exists
        expected_output = self.temp_path / "auto_test_compressed.jpg"
        assert expected_output.exists()

    def test_compress_single_image_function(self):
        """Test the _compress_single_image helper function."""
        input_path = self.create_test_image("helper_test.jpg", (1600, 1200))
        output_path = self.temp_path / "helper_output.jpg"

        result = _compress_single_image(
            str(input_path), str(output_path), 800, 600, 90, "JPEG", True
        )

        assert result["success"] is True
        assert result["input"] == str(input_path)
        assert result["output"] == str(output_path)
        assert "KB" in result["original_size"]
        assert "KB" in result["new_size"]
        assert isinstance(result["size_reduction"], float)

        # Check actual compression occurred
        with Image.open(output_path) as img:
            assert img.size == (800, 600)

    @pytest.mark.asyncio
    async def test_compress_different_formats(self):
        """Test compression with different output formats."""
        input_path = self.create_test_image("format_test.jpg")

        for format_type in ["JPEG", "PNG", "WebP"]:
            output_path = self.temp_path / f"format_test.{format_type.lower()}"

            arguments = {
                "input_path": str(input_path),
                "output_path": str(output_path),
                "format": format_type,
                "quality": 80
            }

            result = await handle_compress_images(arguments)

            assert len(result) == 1
            assert "successfully" in result[0].text
            assert output_path.exists()

    @pytest.mark.asyncio
    async def test_compress_size_limits(self):
        """Test compression with various size limits."""
        input_path = self.create_test_image("size_test.jpg", (4000, 3000))

        # Test with small limits
        arguments = {
            "input_path": str(input_path),
            "max_width": 200,
            "max_height": 150,
            "output_path": str(self.temp_path / "small_output.jpg")
        }

        result = await handle_compress_images(arguments)

        assert len(result) == 1
        assert "successfully" in result[0].text

        with Image.open(self.temp_path / "small_output.jpg") as img:
            assert img.size == (200, 150)

    @pytest.mark.asyncio
    async def test_compress_quality_settings(self):
        """Test different quality settings affect file size."""
        input_path = self.create_test_image("quality_test.jpg", (1000, 1000))

        high_quality_path = self.temp_path / "high_quality.jpg"
        low_quality_path = self.temp_path / "low_quality.jpg"

        # High quality
        arguments_high = {
            "input_path": str(input_path),
            "output_path": str(high_quality_path),
            "quality": 95
        }

        # Low quality
        arguments_low = {
            "input_path": str(input_path),
            "output_path": str(low_quality_path),
            "quality": 30
        }

        await handle_compress_images(arguments_high)
        await handle_compress_images(arguments_low)

        # Low quality should produce smaller file
        high_size = high_quality_path.stat().st_size
        low_size = low_quality_path.stat().st_size
        assert low_size < high_size