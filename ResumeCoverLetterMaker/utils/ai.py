"""
utils/ai.py

Shared AI logic for keyword extraction and model calls.
"""
import logging
from utils.ollama import generate as ollama_generate

def _call_ollama(prompt: str, system: str, config: dict) -> str:
    model = config.get("local_model", "llama3.2")
    return ollama_generate(prompt, model=model, system=system)

def _call_gemini(prompt: str, config: dict) -> str:
    from google import genai
    client = genai.Client(api_key=config["gemini_api_key"])
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()

_KEYWORD_PROMPT = """Extract the following from this job description:
1. Company Name
2. Job Title
3. Top 8-10 Required Technical Skills (exact terms like "Java", "React", "K8s")
4. Top 3-5 Soft Skills (e.g. "leadership", "communication")

Output ONLY a raw JSON object like this (no markdown fences, no preamble):
{{
  "company_name": "...",
  "job_title": "...",
  "required_skills": ["...", "..."],
  "soft_skills": ["...", "..."]
}}

JOB DESCRIPTION:
{job_text}"""

def extract_keywords(job_text: str, config: dict) -> dict:
    import json
    prompt = _KEYWORD_PROMPT.format(job_text=job_text[:5000])
    
    if config.get("use_local", True):
        raw = _call_ollama(prompt, "You are a JSON extractor.", config)
    else:
        raw = _call_gemini(prompt, config)
        
    try:
        # Clean up possible markdown fences
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        if clean.startswith("json"):
            clean = clean[4:].strip()
            
        return json.loads(clean)
    except Exception as e:
        logging.error(f"Failed to parse JSON: {e}\nRaw output: {raw}")
        return {{}}
