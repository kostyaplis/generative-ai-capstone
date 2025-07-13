"""
Task Classifier

This module classifies user queries to determine which component
should handle the request.
"""

import logging
from typing import Dict, Any, Tuple

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class TaskClassifier:
    """
    Classifies incoming queries to determine the appropriate handling component.

    This classifier uses a combination of keyword matching, pattern recognition,
    and context analysis to determine the best component to handle a user query.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the task classifier.

        Args:
            config: Configuration dictionary for the classifier
        """
        self.config = config
        self.confidence_threshold = config.get("confidence_threshold", 0.7)

        try:
            # Initialize LLM classification chain
            self.system_message = self._create_classification_prompt()

            self.classify_chain = ChatOpenAI(
                model=config["model_name"],
                temperature=config["temperature"],
                api_key=config["openai_key"],
            )
            logger.info("LLM classification initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise RuntimeError("Failed to initialize LLM for TaskClassifier")

        # Task definitions for the LLM
        self.available_tasks = {
            "document_qa": "Answering questions about documents, searching for information in documents, summarizing documents",
            "image_generation": "Generating images, creating pictures, visualizing concepts",
            "agent_task:weather": "Weather forecasts, current weather conditions, temperature checks for locations",
            "agent_task:sql": "Database queries, retrieving or manipulating data in databases",
            "agent_task:recommender": "Recommendation of events, based on weather information for provided location, user preference and event availability in the database",
            "conversation": "General conversation, chitchat, questions that don't fit into other categories",
        }

        logger.info("Task Classifier initialized")

    def classify(
        self, query: str, context: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Classify the user query to determine which component should handle it.
        Uses LLM for classification, considering both the query and conversation context.

        Args:
            query: User query text
            context: Request context including history

        Returns:
            tuple: (task_type, agent_type, task_parameters)
            - task_type: String identifier for the component
            - agent_type: String identifier for the agent
            - task_parameters: Dict of extracted parameters for the task
        """
        try:
            # Prepare context for LLM
            context_text = self._format_context_for_llm(context)
            logger.debug(f"Context for LLM: {context_text}")
            available_tasks = "\n".join(
                [f"- {task}: {desc}" for task, desc in self.available_tasks.items()]
            )
            logger.debug(f"Available tasks for LLM: {available_tasks}")

            # Create a list of messages for the ChatOpenAI model
            messages = [
                {
                    "role": "system",
                    "content": self.system_message.format(
                        context=context_text, available_tasks=available_tasks
                    ),
                },
                {"role": "user", "content": query},
            ]

            # Call the LLM directly with messages
            result = self.classify_chain.invoke(messages)

            # Parse LLM response
            task_type, task_agent, params = self._parse_llm_classification(result)

            logger.info(f"LLM classified query as: {task_type} with params: {params}")
            return task_type, task_agent, params

        except Exception as e:
            logger.error(f"Error in LLM classification: {e}", exc_info=True)
            raise RuntimeError("Failed to classify query")

    def _create_classification_prompt(self) -> str:
        """Create the prompt template for task classification."""
        return """You are an AI task classifier. Your job is to determine which component should handle a user query.

        Available task categories:
        {available_tasks}

        User's conversation history and context:
        {context}

        Analyze the user's query carefully, then respond with a JSON object containing:
        1. The most appropriate task category from the list above
        2. Any detected parameters needed for the task (e.g., location for weather or location for the event recommendation)

        Response format must be valid JSON with task field and params object. Example:
        {{"task": "agent_task:weather", "params": {{"location": "New York"}}}}

        Example for event recommendation:
        {{"task": "agent_task:recommender", "params": {{"location": "Singapore"}}}}
        """

    def _format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format the context for the LLM prompt."""
        context_text = ""

        # Add conversation history if available
        history = context.get("history", [])
        logger.debug(f"Conversation history: {history}")

        # if history:
        #     context_text += "Recent conversation:\n"
        #     # Limit to last 3 interactions for brevity
        #     for interaction in history[-3:]:
        #         user_query = interaction.get("user_query", "")
        #         assistant_response = interaction.get("assistant_response", "")
        #         context_text += f"User: {user_query}\n" if user_query else ""
        #         context_text += f"Assistant: {assistant_response}\n" if assistant_response else ""

        # Add any other context that might be relevant
        if "document_context" in context:
            context_text += "\nThe user has been discussing documents recently.\n"

        if "image_context" in context:
            context_text += "\nThe user has been generating images recently.\n"

        return context_text

    def _parse_llm_classification(self, llm_output) -> Tuple[str, str, Dict[str, Any]]:
        """Parse the output from the LLM classification."""
        try:
            import json

            logger.debug(f"LLM output {type(llm_output)}: {llm_output}")

            # Extract content from AIMessage
            if hasattr(llm_output, "content"):
                content = llm_output.content
            else:
                logger.warning(f"Unexpected LLM output type: {type(llm_output)}")
                return "conversation", "", {}

            # Parse the JSON response
            try:
                json_output = json.loads(content)
                task = json_output.get("task")
                params = json_output.get("params", {})
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from LLM output: {content}")
                return "conversation", "", {}

            # Check if task is valid
            if not task:
                logger.error(f"No task specified in LLM output: {content}")
                return "conversation", "", {}

            if task not in self.available_tasks:
                logger.error(f"Unrecognized task type from LLM: {task}")
                return "conversation", "", {}

            # Handle agent tasks which have a prefix
            if task.startswith("agent_task:"):
                task_type = "agent_task"
                agent_type = task.split(":")[1]
            else:
                task_type = task
                agent_type = ""

            # Return the parsed results
            logger.debug(
                f"Parsed task: {task_type}, agent: {agent_type}, params: {params}"
            )
            return task_type, agent_type, params

        except Exception as e:
            logger.error(f"Error parsing LLM classification: {e}", exc_info=True)
            return "conversation", "", {}
