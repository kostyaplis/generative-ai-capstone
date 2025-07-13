"""
Memory Storage Module

This module provides storage functionality for conversation memory.
"""

import logging
import os
import json
import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MemoryStorage:
    """
    Manages storage and retrieval of conversation data.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the memory storage system.

        Args:
            config: Configuration dictionary for storage settings
        """
        self.config = config
        self.storage_type = config.get("storage_type", "file")
        self.storage_dir = config.get("storage_dir", "data/conversation_logs")

        # Ensure the storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)

        logger.info(f"Memory Storage initialized with type: {self.storage_type}")

    def save_conversation(
        self, conversation_id: str, conversation_data: Dict[str, Any]
    ) -> bool:
        """
        Save conversation data to storage.

        Args:
            conversation_id: ID of the conversation
            conversation_data: Full conversation data

        Returns:
            Boolean indicating success
        """
        if self.storage_type == "file":
            return self._save_to_file(conversation_id, conversation_data)
        else:
            logger.warning(f"Unsupported storage type: {self.storage_type}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation data from storage.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Conversation data dictionary or None if not found
        """
        if self.storage_type == "file":
            return self._load_from_file(conversation_id)
        else:
            logger.warning(f"Unsupported storage type: {self.storage_type}")
            return None

    def get_conversations_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all conversations for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of conversation data dictionaries
        """
        if self.storage_type == "file":
            return self._load_user_conversations_from_file(user_id)
        else:
            logger.warning(f"Unsupported storage type: {self.storage_type}")
            return []

    def _save_to_file(
        self, conversation_id: str, conversation_data: Dict[str, Any]
    ) -> bool:
        """Save conversation data to a JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            with open(file_path, "w") as f:
                json.dump(conversation_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving conversation to file: {e}", exc_info=True)
            return False

    def _load_from_file(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data from a JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            if not os.path.exists(file_path):
                return None

            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation from file: {e}", exc_info=True)
            return None

    def _load_user_conversations_from_file(self, user_id: str) -> List[Dict[str, Any]]:
        """Load all conversations for a user from file storage."""
        conversations = []

        try:
            # Check all JSON files in the storage directory
            for filename in os.listdir(self.storage_dir):
                if not filename.endswith(".json"):
                    continue

                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, "r") as f:
                        conversation = json.load(f)
                        if conversation.get("user_id") == user_id:
                            conversations.append(conversation)
                except Exception as e:
                    logger.error(f"Error reading file {filename}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error listing conversation files: {e}", exc_info=True)

        # Sort by updated_at timestamp, most recent first
        conversations.sort(
            key=lambda x: datetime.datetime.fromisoformat(
                x.get("updated_at", "1970-01-01T00:00:00")
            ),
            reverse=True,
        )

        return conversations
