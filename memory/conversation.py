"""
Conversation Memory Module

This module handles the storage and retrieval of conversation history,
providing context for the AI assistant.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
import datetime
import os

from memory.storage import MemoryStorage

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history for contextual responses.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the conversation memory manager.

        Args:
            config: Configuration dictionary for memory settings
        """
        self.config = config
        self.storage_type = config.get("storage_type", "file")
        self.max_history: int = config.get("max_history", 20)
        self.storage = MemoryStorage(config)

        # Ensure storage directory exists
        self._ensure_storage_dir()

        logger.info("Conversation Memory initialized")

    def _ensure_storage_dir(self):
        """Ensure the storage directory exists."""
        storage_dir = self.config.get("storage_dir", "data/conversation_logs")
        os.makedirs(storage_dir, exist_ok=True)

    def create_conversation(self, user_id: str) -> str:
        """
        Create a new conversation and return its ID.

        Args:
            user_id: ID of the user starting the conversation

        Returns:
            String conversation ID
        """
        conversation_id = str(uuid.uuid4())

        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "interactions": [],
        }

        self.storage.save_conversation(conversation_id, conversation_data)
        logger.info(f"Created new conversation: {conversation_id} for user: {user_id}")

        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a full conversation by ID.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Conversation data as a dictionary
        """
        return self.storage.get_conversation(conversation_id)

    def get_conversation_history(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent interactions from a conversation.

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of interactions to retrieve (newest first)

        Returns:
            List of interaction dictionaries
        """
        if limit is None:
            limit = self.max_history

        conversation = self.storage.get_conversation(conversation_id)
        if conversation is None:
            logger.warning(f"Conversation not found: {conversation_id}")
            return []

        interactions = conversation.get("interactions", [])
        # Return most recent interactions first
        return interactions[-limit:]

    def add_interaction(
        self,
        conversation_id: str,
        user_query: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a new interaction to a conversation.

        Args:
            conversation_id: ID of the conversation
            user_query: Text of the user's query
            assistant_response: Text of the assistant's response
            metadata: Optional metadata about the interaction

        Returns:
            Boolean indicating success
        """
        if metadata is None:
            metadata = {}

        conversation = self.storage.get_conversation(conversation_id)
        if not conversation:
            logger.warning(
                f"Cannot add interaction: Conversation not found: {conversation_id}"
            )
            return False

        # Create new interaction
        interaction = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query": user_query,
            "assistant_response": assistant_response,
            "metadata": metadata,
        }

        # Add to conversation
        conversation["interactions"].append(interaction)
        conversation["updated_at"] = datetime.datetime.now().isoformat()

        # Save updated conversation
        self.storage.save_conversation(conversation_id, conversation)
        logger.debug(f"Added interaction to conversation: {conversation_id}")

        return True

    def search_conversations(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant past conversations.

        Args:
            user_id: ID of the user
            query: Search query

        Returns:
            List of matching interaction dictionaries
        """
        # Get all conversations for this user
        conversations = self.storage.get_conversations_by_user(user_id)

        matches = []
        for conversation in conversations:
            for interaction in conversation.get("interactions", []):
                # Simple keyword matching (could be improved with semantic search)
                if (
                    query.lower() in interaction["user_query"].lower()
                    or query.lower() in interaction["assistant_response"].lower()
                ):
                    matches.append(
                        {
                            "conversation_id": conversation["id"],
                            "timestamp": interaction["timestamp"],
                            "interaction": interaction,
                        }
                    )

        # Sort by timestamp, most recent first
        matches.sort(key=lambda x: x["timestamp"], reverse=True)

        return matches[:10]  # Return top 10 matches
