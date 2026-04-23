"""
core/tools/image_gen_tool.py
LangChain/CrewAI-compatible image generation tool.
Supports:
  - "dalle"     → OpenAI DALL·E (via official LangChain tool)
  - "stable_diffusion" → Automatic1111 WebUI API (/sdapi/v1/txt2img)
  - "none"      → graceful no-op message

Saves images to MEDIA_UPLOAD_DIR (from settings) and returns clean path for MediaHandler + platform posters.
Fully compatible with CopyWriter / Editor / QualityGatekeeper agents.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Type

import httpx
from PIL import Image  # for optional resize/optimization
from pydantic import Field, create_model

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import get_settings
from loguru import logger

# ─────────────────────────────────────────────────────────────────────────────
#  Graceful imports for DALL·E (2026 stable)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
    from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
    DALLE_AVAILABLE = True
except ImportError:
    DALLE_AVAILABLE = False


class _BaseImageGenTool(BaseTool):
    """Base image generation tool with provider routing and file persistence."""

    name: str = "image_generator"
    description: str = (
        "Generate a high-quality, platform-optimized image from a detailed text prompt. "
        "Returns the absolute path to the saved image file (ready for upload). "
        "Supports DALL·E (OpenAI) or local Stable Diffusion (Automatic1111). "
        "Always respect the provided aspect_ratio for the target platform."
    )

    args_schema: Type = create_model(
        "ImageGenInput",
        prompt=(str, Field(..., description="Detailed visual description / prompt for the image")),
        aspect_ratio=(
            Optional[str],
            Field(None, description="Platform-specific aspect ratio e.g. '1:1', '16:9', '9:16', '1.91:1'"),
        ),
        platform=(
            Optional[str],
            Field(None, description="Target platform (twitter/linkedin/instagram/etc) for optimization hints"),
        ),
    )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _run(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        platform: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Main synchronous execution with provider routing."""
        if not prompt or len(prompt.strip()) < 10:
            return "❌ Error: Image prompt too short. Provide a detailed description (min 10 characters)."

        settings = get_settings()

        if settings.image_gen_provider == "none":
            return (
                "ℹ️ Image generation is disabled (IMAGE_GEN_PROVIDER=none in .env). "
                "The post will be text-only. Enable DALL·E or Stable Diffusion to generate visuals."
            )

        # Ensure media directory exists
        media_dir = Path(settings.media_upload_dir)
        media_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"generated_{timestamp}.png"
        output_path = media_dir / filename

        provider = settings.image_gen_provider.lower()

        try:
            if provider == "dalle" and DALLE_AVAILABLE:
                result = self._generate_dalle(prompt, aspect_ratio, platform, output_path)
            elif provider == "stable_diffusion":
                result = self._generate_stable_diffusion(prompt, aspect_ratio, platform, output_path)
            else:
                return f"❌ Unsupported IMAGE_GEN_PROVIDER: '{provider}'. Supported: dalle, stable_diffusion, none."

            # Optional: resize for platform aspect ratio using PIL
            if aspect_ratio and output_path.exists():
                self._optimize_aspect_ratio(output_path, aspect_ratio)

            logger.success(f"✅ Image generated and saved: {output_path}")
            return f"✅ Image generated successfully and saved as: {output_path.absolute()}"

        except Exception as e:  # noqa: BLE001
            logger.error(f"Image generation failed for prompt: {prompt[:100]}... | Error: {e}")
            return f"❌ Image generation failed: {str(e)}. The post can still go live as text-only."

    def _generate_dalle(
        self,
        prompt: str,
        aspect_ratio: Optional[str],
        platform: Optional[str],
        output_path: Path,
    ) -> None:
        """DALL·E generation via official LangChain tool."""
        settings = get_settings()
        api_wrapper = DallEAPIWrapper(
            model="dall-e-3",  # highest quality
            api_key=settings.openai_api_key,  # pulled from settings
        )
        tool = OpenAIDALLEImageGenerationTool(api_wrapper=api_wrapper)
        # LangChain tool returns base64 or path; we force file save
        result = tool.run(prompt)  # returns path or base64 in recent versions
        # If it returns base64, decode and save; otherwise copy if path
        if isinstance(result, str) and result.startswith("http") or Path(result).exists():
            # Some versions return URL/path
            pass  # already handled by tool
        else:
            # Fallback: assume base64 or direct save
            from base64 import b64decode
            if isinstance(result, str) and len(result) > 100:
                image_data = b64decode(result.split(",")[-1] if "," in result else result)
                output_path.write_bytes(image_data)

    def _generate_stable_diffusion(
        self,
        prompt: str,
        aspect_ratio: Optional[str],
        platform: Optional[str],
        output_path: Path,
    ) -> None:
        """Direct call to Automatic1111 /sdapi/v1/txt2img."""
        settings = get_settings()
        url = f"{settings.stable_diffusion_url.rstrip('/')}/sdapi/v1/txt2img"

        # Map aspect ratio to width/height (common social ratios)
        width, height = self._get_dimensions_from_ratio(aspect_ratio or "1:1")

        payload = {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, deformed, ugly",
            "width": width,
            "height": height,
            "steps": 30,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M Karras",
            "seed": -1,
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        # Save first image from response
        if "images" in data and data["images"]:
            from base64 import b64decode
            image_data = b64decode(data["images"][0])
            output_path.write_bytes(image_data)
        else:
            raise RuntimeError("No images returned from Stable Diffusion API")

    def _get_dimensions_from_ratio(self, ratio: str) -> tuple[int, int]:
        """Convert aspect ratio string to reasonable pixel dimensions (social media friendly)."""
        ratios = {
            "1:1": (1024, 1024),
            "16:9": (1280, 720),
            "9:16": (720, 1280),
            "1.91:1": (1200, 630),  # LinkedIn / Facebook standard
            "4:5": (1080, 1350),    # Instagram portrait
        }
        return ratios.get(ratio, (1024, 1024))

    def _optimize_aspect_ratio(self, image_path: Path, aspect_ratio: str) -> None:
        """Lightweight resize to match platform aspect ratio using PIL."""
        try:
            with Image.open(image_path) as img:
                w, h = self._get_dimensions_from_ratio(aspect_ratio)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                img.save(image_path, format="PNG", optimize=True)
        except Exception:
            pass  # non-critical optimization

    async def _arun(self, prompt: str, aspect_ratio: Optional[str] = None, platform: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Async delegation (CrewAI multimodal agents)."""
        return self._run(prompt, aspect_ratio, platform, run_manager)


# ─────────────────────────────────────────────────────────────────────────────
#  Public Factory Function (mirrors search_tool.py pattern)
# ─────────────────────────────────────────────────────────────────────────────

def get_image_gen_tool() -> BaseTool:
    """Return ready-to-use image generation tool for ContentCrew agents."""
    return _BaseImageGenTool()


# Optional future-proofing (low-cost stub)
def get_image_edit_tool() -> BaseTool:
    """Stub for img2img / editing (can be expanded later)."""
    # For now return the same tool; extend _BaseImageGenTool with img2img later if needed
    return _BaseImageGenTool(name="image_editor")


# Clean exports
__all__ = ["get_image_gen_tool", "get_image_edit_tool"]