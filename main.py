#!/usr/bin/env python3
"""
AI Assistant Integration Demo - Main Entry Point

This script demonstrates the AI Assistant's capabilities by simulating
different types of requests and showing the responses.
"""

import logging

# Import the controller and utilities
from controller.router import RequestRouter
from config import load_config

# Setup logging
logger = logging.getLogger(__name__)


def display_response(response):
    """Format and display a response from the AI Assistant."""
    logger.debug(f"Response: {response}")

    print("\n" + "=" * 50)
    print("RESPONSE:")
    print("-" * 50)

    if isinstance(response.get("content"), dict):
        print(response["content"]["response"])
    else:
        print(response.get("content", "No content"))

    print("-" * 50)
    print(f"Task type: {response.get('task_type', 'unknown')}")
    print(f"Components used: {', '.join(response.get('components_used', ['unknown']))}")
    print(f"Conversation ID: {response.get('conversation_id', 'none')}")
    print("=" * 50 + "\n")


def main():
    """Run the demonstration."""
    # Load configuration
    config = load_config()

    # Initialize the request router
    router = RequestRouter(config)

    # Test user ID
    user_id = "demo_user"
    conversation_id = None

    print("\n🤖 AI ASSISTANT INTEGRATION DEMO 🤖\n")
    print(
        "This demo will showcase different capabilities of the integrated AI Assistant."
    )

    # Demonstration 1: Conversation
    print("\n📝 DEMONSTRATION 1: Conversation with Memory")
    query = "Hello! My name is Demo User. How are you today?"
    print(f"\nUser: {query}")

    response = router.process_request(query=query, user_id=user_id)
    conversation_id = response["conversation_id"]
    display_response(response)

    # Follow-up conversation
    query = "What can you help me with?"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Follow-up conversation
    query = "Do you remember my name?"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Demonstration 2: Weather Agent
    print("\n🌦️ DEMONSTRATION 2: Weather Information")
    query = "What's the weather like in San Francisco?"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Demonstration 3: Event Recommender Agent
    print("\n🎭 DEMONSTRATION 3: Event Recommendations")
    query = "What events are happening in Singapore today? I prefer outdoor activities if the weather is nice."
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Demonstration 4: Document QA
    print("\n🔍 DEMONSTRATION 4: Document Question-Answering")
    query = "What is the main purpose of the AI Usage Policy document?"
    print(f"\nUser: {query}\n")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Follow-up Document QA question
    print("\n🔍 Follow-up Document Question")
    query = "What are the key responsibilities for employees using AI according to the policy?"
    print(f"\nUser: {query}\n")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Follow-up Document QA question
    print("\n🔍 Follow-up Document Question")
    query = "Provide me the list of approved AI tools"
    print(f"\nUser: {query}\n")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Demonstration 5: Image Generation with LLM-enhanced prompts
    print("\n🌟 DEMONSTRATION 5: Image Generation with LLM-enhanced Prompts")
    print("Note: This feature requires an OpenAI API key with DALL-E access enabled")

    # Example 1: Basic image generation
    query = "Generate an image of a futuristic cityscape with flying cars"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Example 2: Image generation with specific style
    print("\n🌟 Style-specific Image Generation")
    query = "Create a painting of a serene mountain landscape at sunset"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    # Demonstration 6: SQL Query
    print("\n💾 DEMONSTRATION 6: Database Query")
    query = "Run a SQL query to get all users sorted by age"
    print(f"\nUser: {query}")

    response = router.process_request(
        query=query, user_id=user_id, conversation_id=conversation_id
    )
    display_response(response)

    print("\n✅ DEMO COMPLETE")
    print(
        "The above demonstrations show how all components are integrated into a single AI assistant."
    )
    print(
        "The system automatically classified each query and routed it to the appropriate component."
    )
    print(
        "Conversation history was maintained throughout to provide context for responses."
    )


if __name__ == "__main__":
    main()
