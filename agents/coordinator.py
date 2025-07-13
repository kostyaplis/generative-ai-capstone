"""
Agent Coordinator

This module coordinates between different specialized agents,
routing tasks to the appropriate agent and handling communication.
"""

import logging
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from agents.weather_agent import WeatherAgent
from agents.sql_agent import SQLAgent
from agents.recommender_agent import RecommenderAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Coordinates between specialized agents and handles task routing.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent coordinator.

        Args:
            config: Configuration dictionary for coordinator settings
        """
        self.config = config

        # Initialize specialized agents
        self.agents = {
            "weather": WeatherAgent(config),
            "sql": SQLAgent(config),
            "recommender": RecommenderAgent(config),
        }

        # Initialize LLM for conversation handling
        self.llm = ChatOpenAI(
            model=config["model_name"],
            temperature=config["temperature"],
            api_key=config["openai_key"],
        )

        logger.info(
            "Agent Coordinator initialized with agents: "
            + ", ".join(self.agents.keys())
        )

    def handle_task(
        self,
        agent_type: str,
        query: str,
        params: Dict[str, Any] = {},
        context: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """
        Route a task to the appropriate specialized agent.

        Args:
            agent_type: Type of agent to handle the task
            query: User query text
            params: Optional parameters for the agent
            context: Optional additional context

        Returns:
            Response from the agent
        """

        # Check if agent type exists
        if agent_type not in self.agents:
            logger.warning(f"Agent type not found: {agent_type}")
            return {
                "response": f"I'm sorry, but I don't have a {agent_type} capability.",
                "success": False,
                "error": f"Agent type not found: {agent_type}",
            }

        try:
            # Route to appropriate agent
            agent = self.agents[agent_type]
            logger.info(f"Routing task to {agent_type} agent")
            logger.info(f"Task parameters: {params}")
            logger.info(f"Context: {context}")

            result = agent.process(query=query, params=params, context=context)

            return {
                "response": result["response"],
                "data": result.get("data"),
                "success": True,
                "agent_type": agent_type,
            }

        except Exception as e:
            logger.error(
                f"Error handling task with agent {agent_type}: {e}", exc_info=True
            )
            return {
                "response": f"I encountered an error while processing your {agent_type} request: {str(e)}",
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
            }

    def handle_conversation(self, query: str, context: Dict[str, Any] = {}) -> str:
        """
        Handle general conversation that doesn't require specialized agents.

        Args:
            query: User query text
            context: Conversation context

        Returns:
            Response text
        """

        # For simple implementation, we'll use a language model directly
        # In a more complex system, this would use a dedicated conversation agent
        try:
            history = context.get("history", [])

            # Format conversation history
            formatted_history = self._format_conversation_history(history)

            # Construct the prompt for the LLM
            system_message = "You are a helpful AI assistant that responds to user queries in a conversational manner."

            if formatted_history:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            system_message + "\n\nConversation history:\n{history}",
                        ),
                        ("user", "{query}"),
                    ]
                )
                response = self.llm.invoke(
                    prompt.format(history=formatted_history, query=query)
                )
            else:
                # Basic conversation without history
                prompt = ChatPromptTemplate.from_messages(
                    [("system", system_message), ("user", "{query}")]
                )
                response = self.llm.invoke(prompt.format(query=query))

            # Extract the content from the LLM response and ensure it's a string
            content = response.content
            logger.debug(f"LLM response content of type {type(content)}: {content}")
            if not isinstance(content, str):
                # Handle case where response is a list or dict
                if isinstance(content, (list, dict)):
                    import json

                    content = json.dumps(content)
                else:
                    content = str(content)
            return content

        except Exception as e:
            logger.error(f"Error handling conversation: {e}", exc_info=True)
            return f"I'm sorry, I encountered an error while processing your message: {str(e)}"

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Format conversation history for use in prompts.

        Args:
            history: List of conversation interactions

        Returns:
            Formatted history string
        """
        if not history:
            return ""

        formatted = "Here's our recent conversation history:\n"

        for interaction in history:
            formatted += f"User: {interaction.get('user_query', '')}\n"
            formatted += f"Assistant: {interaction.get('assistant_response', '')}\n\n"

        return formatted
