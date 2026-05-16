import os
import yaml
from typing import Dict, Any

def load_user_config() -> Dict[str, Any]:
    """
    Loads the user configuration from the mounted YAML file.
    Returns an empty dict if the file is not found or invalid.
    """
    config_path = "/app/user_config.yaml"
    
    if not os.path.exists(config_path):
        # Fallback for local development outside docker if needed
        config_path = os.path.join(os.path.dirname(__file__), "../../../ResumeCoverLetterMaker/config-kushal.yaml")
        if not os.path.exists(config_path):
            print(f"Warning: Configuration file not found at {config_path}")
            return {}

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading user configuration: {e}")
        return {}

def get_user_context_string() -> str:
    """
    Returns a string representation of the user's personal details
    to be injected into LLM prompts.
    """
    config = load_user_config()
    personal = config.get("personal", {})
    
    if not personal:
        return "No specific user profile available."
    
    context = f"Applicant Name: {personal.get('name')}\n"
    context += f"Email: {personal.get('email')}\n"
    context += f"Phone: {personal.get('phone')}\n"
    context += f"LinkedIn: {personal.get('linkedin')}\n"
    context += f"Location: {personal.get('location')}\n"
    
    # Optionally add more context if needed (e.g. skills from elsewhere in config)
    return context
