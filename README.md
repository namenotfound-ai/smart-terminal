
## Environment

```bash
# Create a new conda environment with Python 3.10
conda create -n wendell_env python=3.10 -y

# Activate the environment
conda activate wendell_env

# Install the required packages
conda install -c conda-forge fastapi uvicorn requests pydantic -y

# Install mlx-lm (this might need to be installed via pip as it's not in conda)
pip install mlx-lm
```