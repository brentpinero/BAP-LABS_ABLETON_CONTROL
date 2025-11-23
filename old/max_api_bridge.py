#!/usr/bin/env python3
"""
Max for Live <-> Flask API Bridge
Accepts commands via stdin, sends HTTP requests, returns JSON via stdout
This allows Max to communicate with the Flask API server
"""
import sys
import json
import requests

API_URL = "http://localhost:8080"

def check_health():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {"status": "success", "server": "healthy", "model_loaded": data.get("model_loaded", False)}
        else:
            return {"status": "error", "message": f"Server returned {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def generate_preset(description):
    """Generate preset from text description"""
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={"description": description},
            timeout=60  # AI generation can take 20-30 seconds
        )

        if response.status_code == 200:
            preset_data = response.json()
            return {"status": "success", "preset": preset_data}
        else:
            return {"status": "error", "message": f"Server returned {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def main():
    """Main loop - read commands from stdin, write responses to stdout"""
    # Read command from stdin
    for line in sys.stdin:
        try:
            command = json.loads(line.strip())
            action = command.get("action")

            if action == "health":
                result = check_health()
            elif action == "generate":
                description = command.get("description", "")
                result = generate_preset(description)
            else:
                result = {"status": "error", "message": f"Unknown action: {action}"}

            # Write result to stdout (Max will read this)
            print(json.dumps(result), flush=True)

        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}), flush=True)
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}), flush=True)

if __name__ == "__main__":
    main()
