"""
Event Recommender Agent

This module provides event recommendations based on weather conditions,
user preferences, and available events in a location.
"""

import logging
import sqlite3
import os
from typing import Dict, Any, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from agents.weather_agent import WeatherAgent

logger = logging.getLogger(__name__)


class RecommenderAgent:
    """
    Agent for handling event recommendations based on weather and preferences.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the recommender agent.

        Args:
            config: Configuration dictionary for recommender agent settings
        """
        self.config = config

        # Initialize database path
        self.db_path = os.path.join(config["agents"]["sql_agent"]["db_path"], "events.db")

        # Initialize weather agent
        self.weather_agent = WeatherAgent(config)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config["model_name"],
            temperature=config["temperature"],
            api_key=config["openai_key"],
        )

        logger.info("Event Recommender Agent initialized")

    def process(
        self, params: Dict[str, Any], query: str = "", context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Process an event recommendation request.

        Args:
            params: Parameters including location and date (optional)
            query: User's original query
            context: Additional context including user preferences

        Returns:
            Dictionary with event recommendations
        """
        try:
            # Extract parameters
            location = params.get("location", "")
            if not location:
                return {
                    "response": "I need a location to recommend events. Please specify a city.",
                    "success": False,
                }

            # Get today's date
            date = datetime.now().strftime("%Y-%m-%d")

            logger.debug(f"Processing event recommendation request for {location} on {date}")

            # Get available events for the location and date
            events = self._get_events_for_location_and_date(location, date)
            if not events:
                return {
                    "response": f"I couldn't find any events in {location} for {date}.",
                    "success": True,
                    "events": [],
                    "weather": {},
                }

            # Get weather data for the location and date
            weather_data = self._get_weather_for_location(location)

            logger.debug(f"type(weather_data): {type(weather_data)}")
            logger.debug(f"Weather data for {location}: {weather_data}")


            # Generate personalized recommendation based on events, weather, and preferences
            recommendation = self._generate_recommendation(
                events, weather_data, location, date, query
            )

            return {
                "response": recommendation,
                "success": True,
                "events": events,
                "weather": weather_data,
            }

        except Exception as e:
            logger.error(f"Error processing recommendation request: {e}", exc_info=True)
            return {
                "response": f"I'm sorry, I couldn't provide event recommendations for {params.get('location', '')}. {str(e)}",
                "success": False,
                "error": str(e),
            }

    def _get_weather_for_location(self, location: str) -> str:
        """
        Get weather data for the specified location.

        Args:
            location: Location name

        Returns:
            Weather data
        """
        params = {"location": location}
        weather_response = self.weather_agent.process(params)

        if "response" in weather_response:
            return weather_response["response"]
        else:
            logger.error(f"Could not get weather data for {location}")
            return ""

    def _get_events_for_location_and_date(self, location: str, date: str) -> List[Any]:
        """
        Query the database for events matching the location and date.

        Args:
            location: Location to find events for
            date: Date to find events for (YYYY-MM-DD)

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Query for events matching the location and date
            c.execute(
                """
                SELECT * FROM events
                WHERE date = ? and city = ?
                """,
                (date, location)
            )
            events = c.fetchall()
            logger.debug(f"Events found for {location} on {date}: {events}")
        except Exception as e:
            logger.error(f"Error querying events database: {e}", exc_info=True)

        finally:
            conn.close()
            return events

    def _generate_recommendation(
        self,
        events: List[Any],
        weather_data: str,
        location: str,
        date: str,
        original_query: str
    ) -> str:
        """
        Generate personalized event recommendations using LLM based on weather and preferences.

        Args:
            events: List of available events
            weather_data: Weather data for the location
            location: Location name
            date: Event date
            original_query: User's original query

        Returns:
            Formatted recommendation text
        """
        try:
            # Format events for LLM
            events_text = ""
            for event in events:
                events_text += f"- {event[1]} (Indoor if {event[2]} else Outdoor): {event[3]} at {event[4]}\n"

            # Create LLM prompt
            prompt = f"""
            You are an AI event recommendation assistant. Based on the following information,
            recommend suitable events for the user in a conversational, helpful tone.

            Location: {location}
            Date: {date}

            Weather information:
            {weather_data}

            Available events:
            {events_text}

            Original user query: \"{original_query}\"

            Please recommend events considering:
            1. Weather conditions (for outdoor events)
            2. User preferences
            3. Event variety (if multiple events are suitable)

            Format your recommendation as a conversational response providing 1-3 specific suggestions,
            explaining why they're good choices based on the weather and preferences.

            If weather data is unavailable, not on this in the response and focus on providing a balanced recommendation of both indoor and outdoor events.
            """

            logger.debug(f"LLM prompt: {prompt}")

            # Call LLM for personalized recommendation
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.invoke(messages)

            # Extract content from LLM response
            try:
                if hasattr(response, "content"):
                    return str(response.content)
                else:
                    logger.error(f"Unexpected LLM response format: {type(response)}")
            except Exception as e:
                logger.error(f"Error extracting content from LLM response: {e}")
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}", exc_info=True)

        return "I'm sorry, I couldn't generate a recommendation based on the available data."
