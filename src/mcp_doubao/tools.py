"""MCP tool definitions for image generation."""

import base64
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent
from PIL import Image

from .doubao_client import DoubaoClient
from .types import GenerateImagesRequest, GenerateImagesResponse
from .config import DEFAULT_SIZE, MAX_IMAGES
from .downloader import ImageDownloader


logger = logging.getLogger(__name__)


def _convert_image_to_base64(image_path: str) -> str:
    """
    Convert a local image file to base64 format for API.

    Image requirements:
    - Format: JPEG, PNG only
    - Aspect ratio: [1/3, 3] (width/height)
    - Min size: > 14px (width and height)
    - Max size: 10MB
    - Max pixels: 6000×6000

    Args:
        image_path: Path to the local image file

    Returns:
        Base64 encoded string in format: data:image/<format>;base64,<base64_data>

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If file is not a valid image or doesn't meet requirements
    """
    image_path_obj = Path(image_path)

    if not image_path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not image_path_obj.is_file():
        raise ValueError(f"Path is not a file: {image_path}")

    # Check file size (max 10MB)
    file_size = image_path_obj.stat().st_size
    max_size_mb = 10
    if file_size > max_size_mb * 1024 * 1024:
        raise ValueError(f"Image file too large: {file_size / (1024 * 1024):.1f}MB (max {max_size_mb}MB)")

    # Get image format from file extension - only JPEG and PNG supported
    suffix = image_path_obj.suffix.lower()
    format_map = {
        '.jpg': 'jpeg',
        '.jpeg': 'jpeg',
        '.png': 'png'
    }

    if suffix not in format_map:
        raise ValueError(f"Unsupported image format: {suffix}. Only JPEG and PNG are supported.")

    image_format = format_map[suffix]

    # Validate image dimensions using PIL
    try:
        with Image.open(image_path) as img:
            width, height = img.size

            # Check minimum size (> 14px for both width and height)
            if width <= 14 or height <= 14:
                raise ValueError(f"Image too small: {width}x{height}px (minimum: 15x15px)")

            # Check maximum pixels (6000x6000)
            if width > 6000 or height > 6000:
                raise ValueError(f"Image too large: {width}x{height}px (maximum: 6000x6000px)")

            # Check aspect ratio [1/3, 3]
            aspect_ratio = width / height
            if aspect_ratio < 1/3 or aspect_ratio > 3:
                raise ValueError(f"Invalid aspect ratio: {aspect_ratio:.2f} (must be between 0.33 and 3.0)")

            logger.info(f"Image validation passed: {width}x{height}px, aspect ratio: {aspect_ratio:.2f}")

    except Exception as e:
        if isinstance(e, ValueError):
            raise  # Re-raise validation errors
        raise ValueError(f"Failed to validate image {image_path}: {str(e)}")

    try:
        # Read and encode the image
        with open(image_path, 'rb') as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/{image_format};base64,{base64_data}"
    except Exception as e:
        raise ValueError(f"Failed to read image file {image_path}: {str(e)}")


# Initialize the Doubao client
_doubao_client = None


def get_doubao_client() -> DoubaoClient:
    """Get or create Doubao client instance."""
    global _doubao_client
    if _doubao_client is None:
        _doubao_client = DoubaoClient()
    return _doubao_client


# MCP Tool definition
GENERATE_IMAGES_TOOL = Tool(
    name="generate_images",
    description="Generate images from text prompts using Doubao AI. Supports multi-image generation: text-to-images (up to 15), single image + text (up to 14), or multi-image + text (2-10 input images, total ≤15).",
    inputSchema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Text description for image generation."
            },
            "num_images": {
                "type": "integer",
                "description": "Number of images to generate (1-3)",
                "minimum": 1,
                "maximum": MAX_IMAGES,
                "default": 1
            },
            "size": {
                "type": "string",
                "description": "Image size specification. Supports two methods (cannot be mixed):\nMethod 1: Resolution preset (1K, 2K, 4K) - specify resolution and describe aspect ratio in prompt, model determines final size.\nMethod 2: Exact pixel dimensions (e.g., 2048x2048) - specify width×height directly.\nDefault: 2048x2048\nPixel range: [1280x720, 4096x4096]\nAspect ratio range: [1/16, 16]\nRecommended sizes:\n1:1 → 2048x2048\n4:3 → 2304x1728\n3:4 → 1728x2304\n16:9 → 2560x1440\n9:16 → 1440x2560\n3:2 → 2496x1664\n2:3 → 1664x2496\n21:9 → 3024x1296",
                "default": DEFAULT_SIZE
            },
            "watermark": {
                "type": "boolean",
                "description": "Whether to add watermark to generated images",
                "default": False
            },
            "output_dir": {
                "type": "string",
                "description": "Absolute path to directory for saving downloaded images. Must be an absolute path (e.g., /Users/username/images or C:\\Users\\username\\images)"
            },
            "image_paths": {
                "type": "array",
                "description": "Optional local file paths to reference images for multi-image generation (1-10 images). Requirements: JPEG/PNG only, size >14px, max 10MB, max 6000×6000px, aspect ratio 1/3-3. Tool auto-converts to base64.",
                "items": {
                    "type": "string",
                    "description": "Absolute path to local image file (JPEG or PNG only)"
                },
                "minItems": 0,
                "maxItems": 10
            },
            "sequential_image_generation": {
                "type": "string",
                "description": "控制是否关闭组图功能。组图：基于您输入的内容，生成的一组内容关联的图片。\n取值范围：\n- auto：自动判断模式，模型会根据用户提供的提示词自主判断是否返回组图以及组图包含的图片数量\n- disabled：关闭组图功能，模型只会生成一张图\n默认值：disabled（默认关闭组图功能）",
                "enum": ["auto", "disabled"],
                "default": "disabled"
            },
            "max_images": {
                "type": "integer",
                "description": "Maximum number of images to generate in sequential mode (1-15). Only effective when sequential_image_generation is set to 'auto'. Total input + output images ≤ 15",
                "minimum": 1,
                "maximum": 15,
                "default": 3
            }
        },
        "required": ["prompt", "output_dir"]
    }
)


# Image compression/resize tool
COMPRESS_IMAGES_TOOL = Tool(
    name="compress_images",
    description="Compress and resize images to optimize for web usage",
    inputSchema={
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Path to the input image file or directory containing images"
            },
            "output_path": {
                "type": "string",
                "description": "Path for the output file or directory (optional, defaults to adding '_compressed' suffix)",
                "default": ""
            },
            "max_width": {
                "type": "integer",
                "description": "Maximum width in pixels (maintains aspect ratio)",
                "minimum": 100,
                "maximum": 4096,
                "default": 1920
            },
            "max_height": {
                "type": "integer",
                "description": "Maximum height in pixels (maintains aspect ratio)",
                "minimum": 100,
                "maximum": 4096,
                "default": 1080
            },
            "quality": {
                "type": "integer",
                "description": "JPEG compression quality (1-100, higher = better quality but larger file)",
                "minimum": 1,
                "maximum": 100,
                "default": 100
            },
            "format": {
                "type": "string",
                "description": "Output image format",
                "enum": ["JPEG", "PNG", "WebP"],
                "default": "JPEG"
            },
            "optimize": {
                "type": "boolean",
                "description": "Enable optimization for smaller file size",
                "default": True
            }
        },
        "required": ["input_path"]
    }
)


async def handle_compress_images(arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Handle the compress_images tool call.

    Args:
        arguments: Tool call arguments from MCP client

    Returns:
        List of TextContent containing the compression results

    Raises:
        ValueError: If arguments are invalid
        Exception: If image compression fails
    """
    try:
        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path", "")
        max_width = arguments.get("max_width", 1920)
        max_height = arguments.get("max_height", 1080)
        quality = arguments.get("quality", 85)
        format_type = arguments.get("format", "JPEG")
        optimize = arguments.get("optimize", True)

        logger.info(f"Compressing images: input={input_path}, max_size={max_width}x{max_height}, "
                   f"quality={quality}, format={format_type}")

        input_path_obj = Path(input_path)

        if not input_path_obj.exists():
            raise ValueError(f"Input path does not exist: {input_path}")

        results = []
        processed_count = 0

        if input_path_obj.is_file():
            # Single file processing
            if not output_path:
                output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_compressed{input_path_obj.suffix}")

            result = _compress_single_image(
                str(input_path_obj), output_path, max_width, max_height, quality, format_type, optimize
            )
            results.append(result)
            if result["success"]:
                processed_count += 1

        elif input_path_obj.is_dir():
            # Directory processing
            output_dir = Path(output_path) if output_path else input_path_obj / "compressed"
            output_dir.mkdir(exist_ok=True)

            # Process all image files in directory
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            for file_path in input_path_obj.iterdir():
                if file_path.suffix.lower() in image_extensions:
                    output_file = output_dir / f"{file_path.stem}_compressed.{format_type.lower()}"
                    result = _compress_single_image(
                        str(file_path), str(output_file), max_width, max_height, quality, format_type, optimize
                    )
                    results.append(result)
                    if result["success"]:
                        processed_count += 1
        else:
            raise ValueError(f"Input path is neither a file nor a directory: {input_path}")

        # Format response
        response_lines = [f"Image compression completed: {processed_count}/{len(results)} images processed successfully"]

        for result in results:
            if result["success"]:
                response_lines.append(
                    f"✓ {result['input']} → {result['output']}\n"
                    f"  Size: {result['original_size']} → {result['new_size']} "
                    f"({result['size_reduction']:.1f}% reduction)"
                )
            else:
                response_lines.append(f"✗ {result['input']}: {result['error']}")

        logger.info(f"Image compression completed: {processed_count}/{len(results)} images processed")

        return [TextContent(
            type="text",
            text="\n".join(response_lines)
        )]

    except ValueError as e:
        logger.error(f"Compression validation error: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: Invalid parameters - {str(e)}"
        )]

    except Exception as e:
        logger.error(f"Image compression error: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: Failed to compress images - {str(e)}"
        )]


def _compress_single_image(input_path: str, output_path: str, max_width: int, max_height: int,
                          quality: int, format_type: str, optimize: bool) -> Dict[str, Any]:
    """
    Compress a single image file.

    Returns:
        Dict containing compression result information
    """
    try:
        # Get original file size
        original_size = os.path.getsize(input_path)

        # Open and process image
        with Image.open(input_path) as img:
            # Convert RGBA to RGB for JPEG format
            if format_type == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            # Calculate new size maintaining aspect ratio
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save with compression
            save_kwargs = {"optimize": optimize}
            if format_type == "JPEG":
                save_kwargs["quality"] = quality
            elif format_type == "WebP":
                save_kwargs["quality"] = quality

            img.save(output_path, format=format_type, **save_kwargs)

        # Get new file size
        new_size = os.path.getsize(output_path)
        size_reduction = ((original_size - new_size) / original_size) * 100

        return {
            "success": True,
            "input": input_path,
            "output": output_path,
            "original_size": f"{original_size / 1024:.1f} KB",
            "new_size": f"{new_size / 1024:.1f} KB",
            "size_reduction": size_reduction
        }

    except Exception as e:
        return {
            "success": False,
            "input": input_path,
            "output": output_path,
            "error": str(e)
        }


async def handle_generate_images(arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Handle the generate_images tool call.

    Args:
        arguments: Tool call arguments from MCP client

    Returns:
        List of TextContent containing the generation results

    Raises:
        ValueError: If arguments are invalid
        Exception: If image generation fails
    """
    try:
        # Extract and validate arguments
        prompt = arguments.get("prompt")
        num_images = arguments.get("num_images", 1)
        size = arguments.get("size", DEFAULT_SIZE)
        watermark = arguments.get("watermark", False)
        output_dir = arguments.get("output_dir")

        # Validate output_dir is provided and is absolute path
        if not output_dir:
            raise ValueError("output_dir is required")

        output_path = Path(output_dir)
        if not output_path.is_absolute():
            raise ValueError(f"output_dir must be an absolute path, got: {output_dir}")
        image_paths = arguments.get("image_paths", [])
        sequential_mode = arguments.get("sequential_image_generation", "disabled")
        max_images = arguments.get("max_images", 3)

        # Convert local image paths to base64
        base64_images = []
        if image_paths:
            logger.info(f"Converting {len(image_paths)} local images to base64")
            for image_path in image_paths:
                try:
                    base64_image = _convert_image_to_base64(image_path)
                    base64_images.append(base64_image)
                    logger.info(f"Converted image: {image_path}")
                except Exception as e:
                    raise ValueError(f"Failed to convert image {image_path}: {str(e)}")

        logger.info(f"Received generate_images request: prompt='{prompt[:50]}...', "
                   f"num_images={num_images}, size={size}, watermark={watermark}, "
                   f"output_dir='{output_dir}', ref_images={len(base64_images)}, "
                   f"sequential_mode={sequential_mode}, max_images={max_images}")

        # Create and validate request
        request = GenerateImagesRequest(
            prompt=prompt,
            num_images=num_images,
            size=size,
            watermark=watermark
        )

        # Get client and generate images
        client = get_doubao_client()
        images = client.generate_images(
            prompt=request.prompt,
            count=request.num_images,
            size=request.size,
            watermark=request.watermark,
            images=base64_images if base64_images else None,
            sequential_mode=sequential_mode,
            max_images=max_images
        )

        # Create response
        response = GenerateImagesResponse(
            images=images,
            count=len(images)
        )

        # Download images to output directory
        logger.info(f"Downloading {response.count} images to: {output_dir}")

        with ImageDownloader() as downloader:
            download_results = downloader.download_images(response.images, output_dir)

        # Format response for MCP
        response_text_lines = [f"Generated {response.count} images:"]

        for i, (image_item, local_path, success) in enumerate(download_results):
            if success:
                response_text_lines.append(
                    f"Image {i+1}: {image_item.url} (size: {image_item.size})\n"
                    f"  → Downloaded to: {local_path}"
                )
            else:
                response_text_lines.append(
                    f"Image {i+1}: {image_item.url} (size: {image_item.size})\n"
                    f"  → Download failed"
                )

        successful_downloads = sum(1 for _, _, success in download_results if success)
        response_text_lines.append(f"\nDownload summary: {successful_downloads}/{response.count} images saved successfully")

        logger.info(f"Successfully generated and downloaded {successful_downloads}/{response.count} images")

        return [TextContent(
            type="text",
            text="\n".join(response_text_lines)
        )]

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: Invalid parameters - {str(e)}"
        )]

    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: Failed to generate images - {str(e)}"
        )]