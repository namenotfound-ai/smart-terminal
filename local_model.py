import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from mlx_lm import load, generate
import traceback

# Initialize FastAPI app
app = FastAPI()

# --- CORS Configuration ---
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---

# 1) Figure out the directory containing this script
try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.getcwd()
    print(f"Warning: __file__ not defined. Using current working directory: {CURRENT_DIR}")

# 2) Load the local MLX model from that directory
MODEL_PATH = CURRENT_DIR
print(f"Attempting to load model from: {MODEL_PATH}")

try:
    model, tokenizer = load(MODEL_PATH)
    print("Model and tokenizer loaded successfully.")
except ValueError as e:
    print(f"Error loading model: {e}")
    print("Please ensure that the model files are correctly placed in the specified directory and are compatible.")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during model loading: {e}")
    print(traceback.format_exc())
    exit(1)

class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = None

@app.post("/ask")
async def ask(req: QuestionRequest):
    """
    Handles a question request, generates an answer using the MLX model.
    The model generation is run in a thread pool to avoid blocking the server's event loop.
    """
    current_prompt = req.question
    max_tokens = req.max_tokens or 128000
    final_prompt = ""

    # Apply chat template if available
    if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template:
        messages = [{"role": "user", "content": current_prompt}]
        try:
            prompt_from_template = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            if isinstance(prompt_from_template, list):
                print("Warning: apply_chat_template returned a list despite tokenize=False. Decoding.")
                final_prompt = tokenizer.decode(prompt_from_template)
            else:
                final_prompt = str(prompt_from_template)
            print(f"Applied chat template. New prompt (first 200 chars): {final_prompt[:200]}...")
        except Exception as e:
            print(f"Error applying chat template: {e}. Using original prompt.")
            print(traceback.format_exc())
            final_prompt = str(current_prompt)
    else:
        final_prompt = str(current_prompt)
        print("No chat template found or applicable. Using raw prompt.")

    print(f"Generating response for prompt (first 100 chars): {final_prompt[:100]}...")

    try:
        answer_text = await run_in_threadpool(
            generate,
            model,
            tokenizer,
            prompt=final_prompt,
            max_tokens=max_tokens,
            verbose=False
        )
        print("Generation successful.")
    except Exception as e:
        print(f"Error during text generation: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to generate answer from model.")

    return {"answer": answer_text}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting Uvicorn server on http://0.0.0.0:5015")
    uvicorn.run(app, host="0.0.0.0", port=5015)
