import os
import json
import requests
import re

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Where your local MLX model is running:
LOCAL_MODEL_URL = os.environ.get("LOCAL_MODEL_URL", "http://localhost:5007/ask")

# ----------------------
# 1. DATA MODELS
# ----------------------

class LLMRequest(BaseModel):
    """
    The payload we receive on POST /chat.
    """
    user_request: str
    system_context: Optional[str] = None
    conversation_history: Optional[str] = None

class LLMCommandSuggestion(BaseModel):
    """
    A single command suggestion from the LLM.
    """
    command: str
    explanation: Optional[str] = None

class LLMResponse(BaseModel):
    """
    The structured response we send back.
    """
    explanation: str
    commands: List[LLMCommandSuggestion]

# ----------------------
# 2. CALLING THE LOCAL MODEL
# ----------------------

def call_local_model_for_commands(prompt: str, max_tokens: int = 512) -> str:
    """
    Calls your local MLX model on port 5007 with a given prompt.
    Returns the raw text 'answer' from the model.
    """
    payload = {"question": prompt, "max_tokens": max_tokens}
    try:
        resp = requests.post(LOCAL_MODEL_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # The MLX endpoint returns: { "answer": "<model output>" }
        return data.get("answer", "")
    except Exception as e:
        print(f"[Error] Could not call local model: {e}")
        return ""

# ----------------------
# 3. OUTPUT SANITIZATION & JSON EXTRACTION
# ----------------------

def sanitize_remove_code_fences(raw_text: str) -> str:
    """
    Removes common markdown fences like ```json ... ``` from the string.
    Also trims leading/trailing whitespace.
    """
    # Remove possible fenced code blocks:
    cleaned = raw_text.replace("```json", "").replace("```", "")
    return cleaned.strip()

def try_json_load(text: str) -> Optional[dict]:
    """
    Safely try to parse text as JSON. Returns a dict if successful, or None if parsing fails.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def extract_json_object_via_regex(text: str) -> Optional[str]:
    """
    Searches the text for the FIRST top-level { ... } block using a
    recursive pattern. Returns it as a string if found, else None.
    """
    # This pattern tries to match a balanced set of curly braces at the top level
    # (using a recursive regex feature).
    # Some Python interpreters might not allow (?R), but let's try:
    pattern = r"\{(?:[^{}]|(?R))*\}"
    match = re.search(pattern, text, flags=re.DOTALL)
    if match:
        return match.group(0)
    return None

def extract_and_parse_json(raw_model_output: str) -> dict:
    """
    Attempt multiple strategies to parse a JSON object from the model output.
    Return a Python dict. If all fail, return an empty dict.
    """
    # 1) Strip code fences
    cleaned = sanitize_remove_code_fences(raw_model_output)

    # 2) Attempt direct json.loads
    parsed = try_json_load(cleaned)
    if parsed is not None:
        return parsed

    # 3) Attempt a regex approach to find the first JSON object
    json_str = extract_json_object_via_regex(cleaned)
    if json_str:
        parsed = try_json_load(json_str)
        if parsed is not None:
            return parsed

    # If we still fail, log the raw output and fallback
    print("[Warning] Could not parse valid JSON. Raw model output below:")
    print(raw_model_output)
    return {}

# ----------------------
# 4. BUILD THE META-PROMPT AND PARSE
# ----------------------

@app.post("/chat", response_model=LLMResponse)
def chat(request: LLMRequest) -> LLMResponse:
    """
    Endpoint: POST /chat
    - Receives user request + optional system context + conversation history
    - Calls local model with a special prompt that demands valid JSON
    - Tries multiple parsing strategies
    - Returns a well-formed LLMResponse (explanation + commands)
    """
    user_text = request.user_request
    history = request.conversation_history or ""
    system = request.system_context or ""

    # 1) Build a strong "JSON only" prompt
    meta_prompt = f"""
You are a command-generation assistant. 
Return VALID JSON with two fields:
1) "explanation" (string)
2) "commands" (array of objects: each has "command" (string) and "explanation" (string))

NO extra text or markdown. NO code fences. Example:

{{
  "explanation": "Steps to install Flask and run a server",
  "commands": [
    {{
      "command": "pip install flask",
      "explanation": "Install Flask"
    }},
    {{
      "command": "python app.py",
      "explanation": "Run the app on port 5000"
    }}
  ]
}}

User request: {user_text}
System context: {system}
Conversation so far: {history}

STRICT FORMAT: Output ONLY that JSON object. No preamble or postamble.
"""

    # 2) Call local model
    raw_model_output = call_local_model_for_commands(meta_prompt, max_tokens=700)
    if not raw_model_output.strip():
        # Fallback if we got nothing
        return LLMResponse(
            explanation="No response from the model or empty string.",
            commands=[]
        )

    # 3) Try extracting JSON from the raw output
    parsed = extract_and_parse_json(raw_model_output)

    # 4) Check the parsed dict for "explanation" and "commands"
    if not parsed:
        # If we have nothing, fallback
        return LLMResponse(
            explanation="Model output was not valid JSON or could not be parsed.",
            commands=[]
        )

    # 5) Extract fields safely
    explanation = parsed.get("explanation", "No explanation provided.")
    commands_data = parsed.get("commands", [])

    # Build the final list of LLMCommandSuggestion
    final_cmds = []
    for c in commands_data:
        cmd_str = c.get("command", "")
        exp_str = c.get("explanation", "")
        final_cmds.append(LLMCommandSuggestion(command=cmd_str, explanation=exp_str))

    return LLMResponse(
        explanation=explanation,
        commands=final_cmds
    )

# ----------------------
# 5. LAUNCH
# ----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
