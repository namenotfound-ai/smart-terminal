
 n a m e n o t f o u n d . a i            

 T H E      
 F U T U R E      
 O F      
 A I      
 I S     
 O N - D E V I C E                     

# Smart Terminal

Transform your command line experience with natural language processing. Smart Terminal allows you to execute complex terminal commands using plain English, powered entirely by local AI models.

## What is Smart Terminal?

Smart Terminal is a locally-running AI system that bridges the gap between natural language and command-line execution. Instead of memorizing complex terminal commands, simply describe what you want to accomplish in plain English, and Smart Terminal will translate, execute, and validate the commands for you.

**Key Features:**
- 🔒 **100% Local**: No internet connection required, no API keys, complete privacy
- 🧠 **Natural Language Interface**: Describe tasks in conversational English
- ⚡ **Instant Execution**: Commands are executed automatically with built-in safety checks
- 🔍 **Transparent Process**: Full visibility into how commands are generated and executed
- 🛡️ **Safety First**: Built-in validation to prevent destructive commands
- 🔧 **Extensible**: Modular architecture for easy customization and expansion

## How It Works

Smart Terminal consists of three interconnected components:

1. **Smart Terminal Frontend** (`smart_terminal.py`): The main interface that handles user input and command execution
2. **LLM Server Middleware** (`llm_server.py`): Orchestrates communication between components and handles request validation
3. **Local Model Backend** (`local_model.py`): Runs the AI model locally using MLX framework

```
User Input → Smart Terminal → LLM Server → Local Model → Command Generation → Execution
```

## Example Use Cases

- **File Operations**: "Find all Python files containing the word 'class' and save the list to a file"
- **Project Setup**: "Create a new directory called 'hello' with a Python script that prints 'Hello World'"
- **System Management**: "Show me all running processes using more than 100MB of memory"
- **Development Tasks**: "Create a virtual environment and install the packages from requirements.txt"

## Video Tutorial
[[LINK HERE]](https://www.loom.com/share/52df96c582ca425d887e37c74f1e2205?sid=3d8e07b5-614d-4190-8e0f-c9b85dabb904)

## Related Tutorial
- Explains conda and phi-4-8bit
[[LINK HERE]](https://www.loom.com/share/51b53e0a7200458a97923b21a0cc2d69?sid=42abe905-25ec-4aa3-adda-4b09e0056c94)

## Requirements

- **Operating System**: macOS (with MLX support)
- **Python**: 3.11+
- **Storage**: ~15GB for the phi-4-8bit model
- **Memory**: 8GB RAM minimum, 16GB recommended

## Environment Setup

1. Set up your local environment
```bash
# Create a new conda environment with Python 3.11
conda create -n smart_terminal_env python=3.11 -y
# Activate the environment
conda activate smart_terminal_env
# Install the required packages
conda install -c conda-forge fastapi uvicorn requests pydantic -y
# Install mlx-lm (this will need to be installed via pip as it's not in conda)
pip install mlx-lm
```

## Local Model Installation

2. Install git-lfs (required for downloading the model):
```bash
# For macOS using Homebrew
brew install git-lfs
# Initialize git-lfs
git lfs install
```

3. Download the phi-4-8bit model:
```bash
# Create a local_models directory
mkdir local_models
cd local_models
# Clone the model repository
# Note: This will download approximately 15GB of model files and may take several minutes
git clone https://huggingface.co/mlx-community/phi-4-8bit --progress
# If you want to clone without large files - just their pointers
# GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/mlx-community/phi-4-8bit
```

## Running the Application

4. Copy the local model configuration:
```bash
# Copy local_model.py into the local model folder for the project you downloaded
cp local_model.py ./local_models/phi-4-8bit/
```

5. Start the services in order:
```bash
# First, start the local model (Terminal 1)
python local_models/phi-4-8bit/local_model.py

# Next, start the LLM server (Terminal 2)
python llm_server.py

# Then, start the smart terminal (Terminal 3)
python smart_terminal.py
```

6. Submit natural language requests to the smart terminal

## Architecture Deep Dive

### Component Communication
- **Smart Terminal** runs on your main terminal session
- **LLM Server** exposes API on `localhost:8001`
- **Local Model** exposes API on `localhost:5015`

### Safety Features
- Command validation before execution
- Destructive command detection and prevention
- User confirmation for potentially dangerous operations
- Sandboxed execution environment

### Extensibility
The modular design allows you to:
- Swap in different local models
- Add custom command validators
- Extend the natural language processing capabilities
- Integrate with other development tools

## Troubleshooting

**Model Download Issues:**
- Ensure git-lfs is properly installed and initialized
- Check available disk space (15GB required)
- Verify internet connection for initial download

**MLX Installation Problems:**
- Ensure you're using macOS with Apple Silicon
- Try installing mlx-lm in a fresh conda environment
- Check Python version compatibility (3.11+ required)

**Port Conflicts:**
- Default ports are 5015 (local model) and 8001 (LLM server)
- Modify port configurations in respective files if conflicts occur

## Contributing

Smart Terminal is designed to be educational and extensible. Contributions are welcome for:
- Additional safety validators
- Support for other local models
- Enhanced natural language processing
- Cross-platform compatibility
- Performance optimizations

## What's Next?

Smart Terminal represents a small piece of a larger vision for local AI-powered development tools. This project demonstrates the foundational concepts that can be extended to:
- Multi-model orchestration
- Complex task automation
- Intelligent code generation and maintenance
- Local AI-powered development environments

The future of AI development tools is local, transparent, and under your control.

## License

Apache License 2.0
