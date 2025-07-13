"""
Weather Agent

This module handles weather-related queries, connecting to
weather APIs to retrieve current conditions and forecasts.
"""

import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)


class WeatherAgent:
    """
    Agent for handling weather-related queries.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the weather agent.

        Args:
            config: Configuration dictionary for weather agent settings
        """
        self.config = config
        self.api_key = config["weather_api_key"]
        self.api_url = config["agents"]["weather_agent"]["api_url"]

        # Check if we have an API key
        if not self.api_key:
            raise ValueError("Weather API key not configured")

        logger.info("Weather Agent initialized")

    def process(
        self, params: Dict[str, Any], query: str = "", context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Process a weather-related query.

        Args:
            params: Required parameters including location

        Returns:
            Dictionary with weather information
        """

        # Extract location from params
        location: str = params.get("location", "")

        try:
            weather_data = self._get_weather(location)

            # Format response
            response_text = self._format_weather_response(location, weather_data)

            return {
                "response": response_text,
                "data": weather_data,
                "location": location,
            }

        except Exception as e:
            logger.error(f"Error processing weather query: {e}", exc_info=True)
            return {
                "response": f"I'm sorry, I couldn't retrieve weather information for {location}. {str(e)}",
                "error": str(e),
            }

    def _get_weather(self, location: str) -> Dict[str, Any]:
        """
        Get weather data from the API.

        Args:
            location: Location name or coordinates

        Returns:
            Weather data
        """

        # Make API request
        params = {"q": location, "key": self.api_key, "aqi": "no"}
        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()

        logger.debug(f"Weather data for {location}: {response.json()}")
        return response.json()

    def _format_weather_response(self, location: str, data: Dict[str, Any]) -> str:
        """
        Format weather data into a user-friendly response.

        Args:
            location: Location name
            data: Weather data

        Returns:
            Formatted response string
        """

        # Extract weather details
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]
        wind_dir = data["current"]["wind_dir"]
        feelslike_c = data["current"]["feelslike_c"]
        time = data["location"]["localtime"]

        return (
            f"Weather in {location}, {data['location']['country']} as of {time}:\n"
            f"  Temperature: {temp_c}°C / {temp_f}°F (feels like {feelslike_c}°C)\n"
            f"  Condition: {condition}\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind: {wind_kph} kph {wind_dir}\n"
        )
