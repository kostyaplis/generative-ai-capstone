"""
Prompt Engine

This module enhances user queries into detailed image generation prompts
using LLM-based prompt engineering techniques.
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class PromptEngine:
    """
    Enhances user queries into detailed image generation prompts.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the prompt engine.

        Args:
            config: Configuration dictionary for prompt engine settings
        """
        self.config = config

        # Initialize LLM for prompt enhancement
        self.llm = ChatOpenAI(
            model=config["model_name"],
            temperature=0.7,  # More creative for prompt enhancement
            api_key=config["openai_key"],
        )

        logger.info("Image Prompt Engine initialized")

    def enhance_prompt(self, query: str) -> str:
        """
        Enhance a user query into a detailed image generation prompt.

        Args:
            query: User query for image generation

        Returns:
            Enhanced prompt for image generation
        """
        try:
            # Create system prompt for enhancing image query
            system_prompt = """
            You are an expert image prompt engineer. Your job is to transform simple image requests
            into detailed, descriptive prompts that will produce high-quality AI-generated images.

            Guidelines for creating great image prompts:
            1. Include details about lighting, perspective, mood, and atmosphere
            2. Specify artistic style, medium, or rendering technique when relevant
            3. Keep the prompt concise but information-dense (under 20 words)
            4. DO NOT include any explanations or commentary - ONLY output the enhanced prompt

            Return ONLY the enhanced prompt, with NO additional text or explanation.

            Example: Digital Art: mountain landscape, morning mist, digital art, 4K concept art, matte painting style, atmospheric perspective
            """

            # Create user prompt that combines the original query with style keywords
            user_prompt = (
                f"Transform this simple image request into a detailed prompt: '{query}'"
            )

            # Get enhanced prompt from LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = self.llm.invoke(messages)

            # Ensure we always return a string
            if hasattr(response, "content"):
                enhanced_prompt = str(response.content)
            else:
                enhanced_prompt = str(response)

            logger.debug(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt

        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return query
