import requests
import json
import os

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://host.docker.internal:11434")

def generate(prompt: str, model: str = "llama3.2", system: str = ""):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    try:
        response = requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return f"Error generating proposal with Ollama: {e}"
