import requests
import subprocess
import json
import os
import re
import socket

# The endpoint for our "command-formatter" server (llm_server.py)
LLM_ENDPOINT = os.environ.get("LLM_SERVER_URL", "http://localhost:8001/chat")


# -----------------------------
# 1. Port Checking Utilities
# -----------------------------
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind(("127.0.0.1", port))
        except socket.error:
            return True
    return False

def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# -----------------------------
# 2. Command Execution
# -----------------------------
def run_shell_command(command: str):
    """
    Runs a shell command and returns (stdout, stderr, returncode).
    """
    print(f"\n[Terminal] Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        code = result.returncode
        return stdout, stderr, code
    except Exception as e:
        return ("", str(e), 1)


# -----------------------------
# 3. Command Interception / Port Checking
# -----------------------------
def maybe_adjust_port_in_command(command: str) -> str:
    """
    If the command references a specific port (like 'python -m http.server 8000'),
    check if that port is free. If not, automatically pick a new free port.
    Returns the possibly modified command.
    """
    # This is a simplistic example matching 'python -m http.server <port>'.
    # You could extend it to match other patterns (like 'flask run --port 8080'),
    # or 'node server.js --port 3000', etc.
    
    # 1) Check if command is something like 'python -m http.server [PORT]'
    pattern = r"python\s+-m\s+http\.server(\s+(\d+))?"
    match = re.search(pattern, command)
    if match:
        # If there's a group(2), that's the port
        port_str = match.group(2)
        if port_str:
            try:
                port = int(port_str)
                if is_port_in_use(port):
                    print(f"[Port Conflict] Port {port} is already in use. Finding a new port.")
                    new_port = get_free_port()
                    # Replace the old port in the command with the new one
                    command = re.sub(rf"{port_str}", str(new_port), command, count=1)
                    print(f"[Info] Command updated to: {command}")
            except ValueError:
                # If we fail to parse, do nothing
                pass
        else:
            # If no port specified (i.e., 'python -m http.server' with no port),
            # we might want to enforce a port. The default is 8000, but let's check if 8000 is free.
            default_port = 8000
            if is_port_in_use(default_port):
                print(f"[Port Conflict] Default port 8000 is in use. Finding a new port.")
                new_port = get_free_port()
                # We'll append the new port
                command += f" {new_port}"
                print(f"[Info] Command updated to: {command}")
    else:
        # If you want to handle other types of commands (e.g., 'flask run -p 8000'),
        # you could add more pattern checks or general logic here.
        pass

    return command

def is_command_dangerous(command: str) -> bool:
    """
    Naive check for extremely dangerous commands.
    """
    lower_cmd = command.lower()
    if "rm -rf /" in lower_cmd:
        return True
    return False


# -----------------------------
# 4. LLM Interaction
# -----------------------------
def get_llm_suggestions(user_request: str, conversation_history: str):
    """
    Send the user request + conversation history to llm_server.py (/chat).
    Expects JSON with fields: "explanation" and "commands".
    """
    payload = {
        "user_request": user_request,
        "conversation_history": conversation_history
    }
    try:
        resp = requests.post(LLM_ENDPOINT, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()  # { "explanation": str, "commands": [ { "command": str, "explanation": str }, ... ] }
        return data
    except Exception as e:
        print(f"[Error] Could not reach LLM server or parse response: {e}")
        return None


# -----------------------------
# 5. Main Loop (Auto-Fix Mode)
# -----------------------------
def main():
    conversation_history = ""
    print("=== Welcome to the Smart Terminal (Auto-Fix Mode) ===")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Call llm_server.py
        llm_data = get_llm_suggestions(user_input, conversation_history)
        if not llm_data:
            print("[Error] No data returned from LLM server.")
            continue

        explanation = llm_data.get("explanation", "")
        commands = llm_data.get("commands", [])

        print(f"\n[LLM Explanation] {explanation}")

        # Run each suggested command automatically
        for cobj in commands:
            cmd = cobj.get("command", "")
            cmd_explanation = cobj.get("explanation", "")

            if cmd_explanation:
                print(f"[LLM Command Explanation] {cmd_explanation}")

            if is_command_dangerous(cmd):
                print(f"[SECURITY WARNING] '{cmd}' is flagged as dangerous. Skipping.")
                continue

            # -- NEW Step: Check for port conflicts before running the command
            cmd = maybe_adjust_port_in_command(cmd)

            # Execute the command
            stdout, stderr, code = run_shell_command(cmd)
            if stdout:
                print(f"[STDOUT]\n{stdout}")
            if stderr:
                print(f"[STDERR]\n{stderr}")

            # If there's an error, automatically attempt to fix
            if code != 0:
                print("[ERROR DETECTED] Return code != 0. Attempting to fix automatically...")

                # We feed the error details back to the LLM
                fix_request = (
                    f"I tried to run '{cmd}' and got this error:\n{stderr}\n"
                    "Please provide a fix or alternative commands to solve the issue. Only respond with JSON."
                )
                fix_data = get_llm_suggestions(fix_request, conversation_history)
                if not fix_data:
                    print("[FIX ERROR] No fix data returned.")
                    continue

                fix_explanation = fix_data.get("explanation", "")
                fix_commands = fix_data.get("commands", [])

                print(f"\n[LLM Fix Explanation] {fix_explanation}")

                for fix_cmd_obj in fix_commands:
                    fix_cmd = fix_cmd_obj.get("command", "")
                    fix_cmd_explanation = fix_cmd_obj.get("explanation", "")
                    if fix_cmd_explanation:
                        print(f"[Fix Command Explanation] {fix_cmd_explanation}")

                    if is_command_dangerous(fix_cmd):
                        print(f"[SECURITY WARNING] Fix command '{fix_cmd}' flagged as dangerous. Skipping.")
                        continue

                    # Again check ports on fix commands
                    fix_cmd = maybe_adjust_port_in_command(fix_cmd)

                    fix_stdout, fix_stderr, fix_code = run_shell_command(fix_cmd)
                    if fix_stdout:
                        print(f"[FIX STDOUT]\n{fix_stdout}")
                    if fix_stderr:
                        print(f"[FIX STDERR]\n{fix_stderr}")

                    if fix_code == 0:
                        print("[FIX] Command executed successfully.")
                    else:
                        print("[FIX ERROR] Command still failing. Stopping auto-fix attempts.")
                        break

        # Update conversation history
        conversation_history += f"\nUser: {user_input}\nLLM Explanation: {explanation}\nCommands: {commands}"


if __name__ == "__main__":
    main()
