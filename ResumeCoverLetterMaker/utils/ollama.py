"""
src/ollama_client.py

Thin wrapper around the Ollama REST API.
Supports both JSON-structured extraction and plain text generation.
"""

import json
import re
import requests


OLLAMA_BASE = "http://localhost:11434"


def _is_running() -> bool:
    """Check if the Ollama daemon is reachable."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def generate(
    prompt: str,
    model: str = "llama3.2",
    system: str = "",
    as_json: bool = False,
    timeout: int = 120,
) -> str:
    """
    Call the Ollama /api/generate endpoint.

    Args:
        prompt:   The user prompt.
        model:    Ollama model name (e.g. 'llama3.2', 'mistral').
        system:   Optional system prompt.
        as_json:  If True, sets Ollama's format=json to force valid JSON output.
        timeout:  Request timeout in seconds (local models can be slow).

    Returns:
        The model's response as a stripped string.

    Raises:
        RuntimeError: If Ollama is not running or returns an error.
    """
    if not _is_running():
        raise RuntimeError(
            "Ollama is not running. Start it with: ollama serve\n"
            "Or run it as a background service: brew services start ollama"
        )

    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system
    if as_json:
        payload["format"] = "json"

    response = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()


def extract_json(
    prompt: str,
    model: str = "llama3.2",
    system: str = "",
    timeout: int = 120,
) -> dict:
    """
    Call Ollama with format=json and parse the response as a dict.
    Strips any accidental markdown fences the model might add.

    Returns:
        Parsed JSON dict.

    Raises:
        ValueError: If the response is not valid JSON.
    """
    raw = generate(prompt, model=model, system=system, as_json=True, timeout=timeout)

    # Strip markdown fences just in case
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON.\nRaw response:\n{raw}"
        ) from exc
