import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from mlx_lm import load, generate

app = FastAPI()

# 1) Figure out the directory containing this script (which presumably also has the model data)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Load the local MLX model from that directory
model, tokenizer = load(CURRENT_DIR)

class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = None

@app.post("/ask")
def ask(req: QuestionRequest):
    prompt = req.question
    max_tokens = req.max_tokens or 128000

    if tokenizer.chat_template:
        messages = [{"role": "user", "content": prompt}]
        prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

    answer_text = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens
    )
    return {"answer": answer_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
