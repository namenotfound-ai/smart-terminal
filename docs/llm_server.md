# LLM Server Documentation

## Overview
The LLM Server is a FastAPI-based service that acts as an intermediary between clients and a local MLX model. It provides a structured way to handle natural language requests and convert them into command suggestions with explanations.

## Architecture

### Components

1. **FastAPI Application**
   - Runs on port 8001 by default
   - Provides a `/chat` endpoint for processing requests

2. **Local MLX Model Integration**
   - Connects to a local MLX model running on port 5015 (configurable via `LOCAL_MODEL_URL` environment variable)
   - Handles communication with the model for command generation

### Data Models

1. **LLMRequest**
   - `user_request`: The main query from the user
   - `system_context`: Optional system-level context
   - `conversation_history`: Optional conversation history

2. **LLMCommandSuggestion**
   - `command`: The suggested command
   - `explanation`: Optional explanation for the command

3. **LLMResponse**
   - `explanation`: Overall explanation of the response
   - `commands`: List of command suggestions

## API Endpoints

### POST /chat

Processes a user request and returns structured command suggestions.

**Request Body:**
```json
{
    "user_request": "string",
    "system_context": "string (optional)",
    "conversation_history": "string (optional)"
}
```

**Response:**
```json
{
    "explanation": "string",
    "commands": [
        {
            "command": "string",
            "explanation": "string"
        }
    ]
}
```

## Key Features

### 1. JSON Response Parsing
The server implements multiple strategies to parse JSON responses from the model:
- Direct JSON parsing
- Code fence removal
- Regex-based JSON object extraction

### 2. Error Handling
- Graceful handling of model communication failures
- Fallback responses for parsing errors
- Timeout handling for model requests

### 3. Meta-Prompting
The server uses a structured meta-prompt to ensure the model returns properly formatted JSON responses with:
- Clear explanation
- Structured command suggestions
- Consistent format

## Usage

1. **Environment Setup**
   ```bash
   export LOCAL_MODEL_URL="http://localhost:5015/ask"  # Optional, defaults to this value
   ```

2. **Starting the Server**
   ```bash
   python llm_server.py
   ```

3. **Making Requests**
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8001/chat",
       json={
           "user_request": "Install Flask and run a server",
           "system_context": "Python environment setup",
           "conversation_history": ""
       }
   )
   ```

## Error Handling

The server implements several fallback mechanisms:
1. Empty model responses return a default message
2. JSON parsing failures return an error message
3. Model communication errors are logged and handled gracefully

## Dependencies

- FastAPI
- Pydantic
- Requests
- Uvicorn

## Configuration

The server can be configured through environment variables:
- `LOCAL_MODEL_URL`: URL of the local MLX model (default: "http://localhost:5015/ask")
