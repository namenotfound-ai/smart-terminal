# Smart Terminal Documentation

## Overview
The Smart Terminal is an intelligent command-line interface that uses an LLM (Large Language Model) to help users execute and fix commands automatically. It provides an interactive environment where users can input natural language requests, and the system will suggest and execute appropriate commands while handling potential errors.

## Features

### 1. Port Management
- Automatically detects port conflicts
- Dynamically assigns free ports when needed
- Currently supports port management for Python's HTTP server
- Extensible for other server types (Flask, Node.js, etc.)

### 2. Command Safety
- Built-in security checks for dangerous commands
- Prevents execution of potentially harmful operations
- Currently checks for dangerous patterns like `rm -rf /`

### 3. LLM Integration
- Communicates with an LLM server for command suggestions
- Maintains conversation history for context
- Provides explanations for suggested commands
- Automatic error fixing capabilities

### 4. Command Execution
- Executes shell commands with proper error handling
- Captures and displays stdout and stderr
- Returns execution status codes

## Architecture

### Core Components

1. **Port Management Utilities**
   - `is_port_in_use(port)`: Checks if a port is already in use
   - `get_free_port()`: Finds an available port
   - `maybe_adjust_port_in_command(command)`: Modifies commands to use available ports

2. **Command Execution**
   - `run_shell_command(command)`: Executes shell commands and returns results
   - Handles stdout, stderr, and return codes

3. **LLM Interaction**
   - `get_llm_suggestions(user_request, conversation_history)`: Communicates with LLM server
   - Expects JSON response with explanations and commands

4. **Safety Checks**
   - `is_command_dangerous(command)`: Validates command safety
   - Prevents execution of harmful commands

## Usage

1. **Starting the Terminal**
   ```bash
   python smart_terminal.py
   ```

2. **Basic Operation**
   - Type your request in natural language
   - The system will:
     - Generate appropriate commands
     - Explain the commands
     - Execute them automatically
     - Handle any errors that occur

3. **Error Handling**
   - If a command fails, the system will:
     - Detect the error
     - Request fix suggestions from the LLM
     - Execute fix commands automatically
     - Continue until success or max attempts reached

4. **Exiting**
   - Type 'exit' or 'quit' to stop the terminal

## Configuration

### Environment Variables
- `LLM_SERVER_URL`: URL of the LLM server (default: "http://localhost:8001/chat")

## Limitations

1. **Port Management**
   - Currently optimized for Python's HTTP server
   - Limited support for other server types

2. **Security**
   - Basic command safety checks
   - May need additional security measures for production use

3. **Error Recovery**
   - Limited to LLM-suggested fixes
   - May not handle all error scenarios

## Future Improvements

1. **Enhanced Port Management**
   - Support for more server types
   - Better port conflict resolution

2. **Security Enhancements**
   - More comprehensive command validation
   - User permission management

3. **Error Handling**
   - More sophisticated error recovery
   - Custom error handling strategies

4. **LLM Integration**
   - Support for multiple LLM providers
   - Improved context management
   - Better command suggestions
