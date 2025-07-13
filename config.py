"""
Configuration Module

This module handles loading and managing configuration settings
for the AI assistant.
"""

import argparse
import logging
import os
from typing import Dict, Any
from pydantic import SecretStr
from dotenv import load_dotenv


# Initialize logger
logger = logging.getLogger(__name__)


# Configure argument parser
def setup_logging():
    """Configure logging based on command line arguments"""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Set verbosity level: -v for INFO, -vv for DEBUG",
    )

    # Parse only known args to avoid conflicts with other argument parsers
    args, _ = parser.parse_known_args()

    # Configure logging format
    logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Set log level based on verbosity count
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO, format=logging_format)
        logger.info("Info logging enabled")
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
        logger.debug("Debug logging enabled")
    else:
        logging.basicConfig(level=logging.WARNING, format=logging_format)


# Set up logging configuration
setup_logging()

DEFAULT_CONFIG = {
    "server": {"host": "0.0.0.0", "port": 8000},
    "task_classifier": {"confidence_threshold": 0.7},
    "model_name": "gpt-4",
    "temperature": 0.0,
    "memory": {
        "storage_type": "file",
        "storage_dir": "data/conversation_logs",
        "max_history": 20,
    },
    "document_qa": {
        "indexer": {
            "documents_dir": "data/documents",
            "db_directory": "data/chroma_db",
            "chunk_size": 1000,
            "chunk_overlap": 200,
        },
        "retriever": {"default_top_k": 5},
    },
    "image_gen": {
        "model_name": "dall-e-3",
        "save_dir": "data/generated_images",
    },
    "agents": {
        "weather_agent": {"api_url": "http://api.weatherapi.com/v1/current.json"},
        "sql_agent": {"db_path": "data/databases"},
        "recommender_agent": {},
    },
}


def load_config() -> Dict[str, Any]:
    """
    Load app configuration defaults.

    Returns:
        Configuration dictionary
    """
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        logger.critical(
            "OPENAI_API_KEY environment variable is not set. Please add it to your .env file."
        )
        raise SystemExit("OPENAI_API_KEY not found. Application cannot start.")

    if not os.getenv("WEATHER_API_KEY"):
        logger.critical(
            "WEATHER_API_KEY environment variable is not set. Please add it to your .env file."
        )
        raise SystemExit("WEATHER_API_KEY not found. Application cannot start.")

    # Load default configuration
    config = DEFAULT_CONFIG.copy()

    # Set API keys
    config["weather_api_key"] = os.getenv("WEATHER_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    config["openai_key"] = (
        SecretStr(openai_api_key) if openai_api_key is not None else None
    )

    return config
