"""
Image Generator

This module handles the generation of images using AI image generation APIs
based on enhanced prompts.
"""

import logging
import os
import requests
from typing import Dict, Any, Optional
import time
import openai

from image_gen.prompt_engine import PromptEngine

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Handles image generation using AI image generation APIs.
    """

    def __init__(
        self, config: Dict[str, Any], prompt_engine: Optional[PromptEngine] = None
    ):
        """
        Initialize the image generator.

        Args:
            config: Configuration dictionary for image generator settings
            prompt_engine: Optional pre-initialized prompt engine
        """
        self.config = config

        # Set up API configuration
        self.api_key = config["openai_key"]
        self.save_dir = config["image_gen"]["save_dir"]
        self.model_name = config["image_gen"]["model_name"]

        # Create image save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)

        # Use provided prompt engine or create new one
        if prompt_engine:
            self.prompt_engine = prompt_engine
        else:
            self.prompt_engine = PromptEngine(config)

        logger.info("Image Generator initialized")

    def generate_image(self, query: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Generate an image based on a user query.

        Args:
            query: User query for image generation
            params: Optional parameters for image generation

        Returns:
            Dictionary with image data and metadata
        """
        try:
            # Enhance the prompt using the prompt engine
            enhanced_prompt = self.prompt_engine.enhance_prompt(query)
            image_data = self._generate_with_openai(enhanced_prompt)

            # Handle successful generation or error response
            if image_data:
                if "url" in image_data:
                    # Image successfully generated
                    image_path = self._save_image(image_data["url"], query)
                    image_data["local_path"] = image_path

                    return {
                        "success": True,
                        "original_query": query,
                        "enhanced_prompt": enhanced_prompt,
                        "image_data": image_data,
                    }
                elif "error" in image_data:
                    # Error was returned from the API
                    logger.error(f"API error: {image_data['error']}")
                    return {"success": False, "error": image_data["error"]}

            logger.error("Failed to generate image, unexpected response format")
            return {
                "success": False,
                "error": "Failed to generate image due to unexpected response format",
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {"success": False, "error": str(e)}

    def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """
        Generate image using OpenAI's DALL-E API.

        Args:
            prompt: Enhanced prompt for image generation

        Returns:
            Dictionary with image data including URL
        """
        try:

            response = openai.images.generate(
                model=self.model_name, prompt=prompt, size="1024x1024", n=1
            )
            # Extract image URL from response
            if response and hasattr(response, "data") and response.data:
                image_url = response.data[0].url
                logger.debug(f"Generated image URL: {image_url}")
                return {"url": image_url}
            else:
                logger.error("Failed to generate image: No image URL found in response")
                return {
                    "error": "Failed to generate image: No image URL found in response"
                }

        except Exception as e:
            if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                logger.error(
                    f"API authorization error: {e}. Please ensure your OpenAI API key has DALL-E access enabled."
                )
                return {
                    "error": "API authorization error. Your API key may not have access to DALL-E image generation."
                }
            else:
                logger.error(f"Error generating image: {e}")
                return {"error": f"Image generation failed: {str(e)}"}

    def _save_image(self, image_url: str, query: str) -> str:
        """
        Download and save image from URL to local file.

        Args:
            image_url: URL of the generated image
            query: Original user query (used for filename)

        Returns:
            Path to saved image file
        """
        try:
            # Create a filename based on timestamp and query
            timestamp = int(time.time())
            safe_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
            filename = f"{timestamp}_{safe_query}.png"
            file_path = os.path.join(self.save_dir, filename)

            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Save image to file
            with open(file_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Image saved to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return ""

    def process(
        self, query: str, params: Dict[str, Any] = {}, context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Process an image generation request.

        Args:
            query: User query for image generation
            params: Optional parameters for image generation
            context: Optional additional context

        Returns:
            Dictionary with generated image data and metadata
        """
        result = self.generate_image(query, params)

        if result.get("success", False):
            return {
                "response": f"Image generated successfully based on: {result['enhanced_prompt']}",
                "image_url": result.get("image_data", {}).get("url", ""),
                "local_path": result.get("image_data", {}).get("local_path", ""),
                "enhanced_prompt": result.get("enhanced_prompt", ""),
                "success": True,
            }
        else:
            return {
                "response": f"Failed to generate image: {result.get('error', 'Unknown error')}",
                "success": False,
                "error": result.get("error", "Unknown error"),
            }
