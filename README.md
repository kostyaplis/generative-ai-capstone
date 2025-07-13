# AI Assistant Integration System
A vibe coding capstone project.

Generative AI: Fundamentals to Advanced Techniques - NUS, March 2025

An integrated AI assistant system with multiple capabilities including conversation handling, document QA, image generation, and specialized agents.

## Features

- **Conversational AI**: Natural language conversations with memory
- **Document QA**: Question-answering on documents
- **Image Generation**: AI-powered image creation with enhanced prompts
- **Weather Information**: Real-time weather data via API
- **Event Recommendations**: Event suggestions based on location and preferences
- **SQL Query Execution**: Run and explain SQL queries

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM and image generation features)
- Weather API key (for weather information)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your-openai-key
   WEATHER_API_KEY=your-weather-api-key
   ```

## Demo

Run the demonstration script to see all features in action:

```bash
python main.py
```

Add verbosity for more detailed logging:
```bash
python main.py -v       # INFO level logging
python main.py -vv      # DEBUG level logging
```

## Project Structure

- **controller/**: Core routing and task classification
- **agents/**: Specialized agents for weather, events, and SQL queries
- **document_qa/**: Document question-answering system
- **image_gen/**: AI image generation with enhanced prompts
- **memory/**: Conversation memory management
- **data/**: Storage for databases, documents, and generated images

## Architecture

The system uses a modular architecture with a central request router that directs queries to appropriate components based on task classification. See the [technical report](technical_report.md) for detailed architecture information.


