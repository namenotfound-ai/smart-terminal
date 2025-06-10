
## Video Tutorial

[LINK HERE]

## Environment

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