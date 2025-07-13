"""
Request Router for AI Assistant

This module handles the routing of incoming requests to the appropriate
components based on intent classification and context.
"""

import logging
from typing import Dict, Any, Optional

# Import task classifier for intent detection
from controller.task_classifier import TaskClassifier

# Import component handlers
from memory.conversation import ConversationMemory
from document_qa.qa_generator import DocumentQA
from image_gen.generator import ImageGenerator
from agents.coordinator import AgentCoordinator

logger = logging.getLogger(__name__)


class RequestRouter:
    """
    Main controller for routing requests to appropriate components.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the request router with all component handlers.

        Args:
            config: Configuration dictionary for all components
        """
        self.config = config

        # Initialize the task classifier
        self.task_classifier = TaskClassifier(config)

        # Initialize component handlers
        self.conversation_memory = ConversationMemory(config)
        self.document_qa = DocumentQA(config)
        self.image_generator = ImageGenerator(config)
        self.agent_coordinator = AgentCoordinator(config)

        logger.info("Request Router initialized with all components")

    def process_request(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming request by:
        1. Classifying the intent
        2. Retrieving relevant context from memory
        3. Routing to appropriate component
        4. Storing the interaction in memory

        Args:
            query: User query text
            user_id: Unique identifier for the user
            conversation_id: Optional conversation identifier
            context: Optional additional context

        Returns:
            Response dictionary with content and metadata
        """
        # Initialize context if None
        if context is None:
            context = {}

        # Get or create conversation ID
        if conversation_id is None:
            conversation_id = self.conversation_memory.create_conversation(user_id)

        # Retrieve conversation history
        history = self.conversation_memory.get_conversation_history(
            conversation_id, limit=10
        )
        context["history"] = history

        # Classify the task
        task_type, agent_type, task_params = self.task_classifier.classify(
            query, context
        )
        logger.info(f"Query classified as: {task_type} : {agent_type}")
        logger.info(f"Task parameters: {task_params}")

        # Route to appropriate component based on task type
        response = self._route_to_component(
            task_type=task_type,
            agent_type=agent_type,
            query=query,
            task_params=task_params,
            context=context,
        )

        # Store interaction in memory
        self.conversation_memory.add_interaction(
            conversation_id=conversation_id,
            user_query=query,
            assistant_response=response.get("content", ""),
            metadata={
                "task_type": task_type,
                "components_used": response.get("components_used", []),
            },
        )

        # Add conversation ID to response
        response["conversation_id"] = conversation_id

        return response

    def _route_to_component(
        self,
        task_type: str,
        agent_type: str,
        query: str,
        task_params: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Route the query to the appropriate component based on task type.

        Args:
            task_type: Type of task identified
            agent_type: Type of agent identified
            query: Original user query
            task_params: Parameters extracted for the task
            context: Request context including history

        Returns:
            Response from the component
        """
        components_used = [task_type]

        if task_type == "document_qa":
            # Get conversation_id from context for maintaining conversation history
            try:
                qa_context = self.document_qa.retrieve_relevant_context(query, top_k=5)
                if qa_context:
                    context["document_context"] = qa_context
                    components_used.append("document_qa")
            except Exception as e:
                logger.warning(f"Error retrieving document context: {e}")

            # conversation_id = context.get("conversation_id")
            response_content = self.document_qa.process(
                query=query, params=task_params, context=context
            )

        elif task_type == "image_generation":
            # Process image generation request through our component
            response_content = self.image_generator.process(query, task_params, context)
            components_used.append("image_gen")

            # If successful, format the response nicely
            if response_content.get("success", False):
                response_content["text"] = (
                    f"Image generated successfully. {response_content.get('response', '')}"
                )
            else:
                response_content["text"] = (
                    f"Failed to generate image: {response_content.get('error', 'Unknown error')}"
                )

            logger.debug(f"Image generation result: {response_content}")

        elif task_type == "agent_task":
            response_content = self.agent_coordinator.handle_task(
                agent_type=agent_type, query=query, params=task_params, context=context
            )
            components_used.append(f"agent:{agent_type}")

        else:  # Default to conversational
            # Get response from conversation handler
            response_content = self.agent_coordinator.handle_conversation(
                query, context
            )

        # Assemble the full response
        response = {
            "content": response_content,
            "components_used": components_used,
            "task_type": task_type,
        }

        return response
