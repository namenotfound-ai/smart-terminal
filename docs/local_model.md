# Local Model API Documentation

## Overview
`local_model_v2.py` is a FastAPI-based server that provides an interface to interact with a local MLX language model. It allows users to send questions to the model and receive generated responses through a REST API endpoint.

## Features
- FastAPI-based REST API
- CORS support for cross-origin requests
- Asynchronous request handling
- MLX model integration
- Chat template support
- Error handling and logging

## API Endpoints

### POST /ask
Sends a question to the local MLX model and returns the generated response.

#### Request Body
```json
{
    "question": "string",
    "max_tokens": "integer (optional)"
}
```

- `question`: The text prompt to send to the model
- `max_tokens`: (Optional) Maximum number of tokens to generate. Defaults to 128000 if not specified.

#### Response
```json
{
    "answer": "string"
}
```

- `answer`: The generated text response from the model

## Technical Details

### Model Loading
- The model is loaded from the same directory as the script
- Uses MLX's `load` function to initialize both model and tokenizer
- Includes error handling for model loading failures

### Chat Template Support
- Automatically applies chat template if available in the tokenizer
- Falls back to raw prompt if template application fails
- Supports both string and list-based template outputs

### Error Handling
- Comprehensive error handling for:
  - Model loading failures
  - Template application errors
  - Text generation errors
- Detailed error logging with stack traces
- HTTP 500 responses for generation failures

### Server Configuration
- Runs on `0.0.0.0:5015`
- Uses Uvicorn as the ASGI server
- Implements CORS middleware for cross-origin requests

## Usage Example

```python
import requests

response = requests.post(
    "http://localhost:5015/ask",
    json={
        "question": "What is machine learning?",
        "max_tokens": 1000
    }
)

print(response.json()["answer"])
```

## Dependencies
- FastAPI
- MLX
- Uvicorn
- Pydantic

## Error Handling
The API implements several layers of error handling:
1. Model loading validation
2. Chat template application error recovery
3. Generation error handling with HTTP exceptions
4. Detailed logging for debugging purposes

## Notes
- The server must be run from a directory containing the MLX model files
- The model generation is run in a thread pool to prevent blocking the server's event loop
- All requests are logged with relevant information for debugging
