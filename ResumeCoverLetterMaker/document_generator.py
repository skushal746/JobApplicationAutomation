"""
document_generator.py

Generates tailored resume, cover letter, and freelance proposal as LaTeX strings.
"""

import os
from utils.ai import _call_ollama, _call_gemini


# ── Project Selection prompt ───────────────────────────────────────────────────
_PROJECT_SELECTION_SYSTEM = (
    "You are a technical recruiter evaluating candidate projects. "
    "You output only the raw Markdown of the selected projects — no commentary, no fences."
)

_PROJECT_SELECTION_PROMPT = """From the provided MY GITHUB PROJECTS list, select the 3-4 most relevant projects for the following job description and keywords.
Return ONLY the raw markdown of the selected projects exactly as they appear in the list.

KEYWORDS:
Required Skills: {required_skills}
Soft Skills: {soft_skills}

JOB DESCRIPTION:
{job_text}

MY GITHUB PROJECTS:
{github_projects_text}"""


# ── Resume prompt ──────────────────────────────────────────────────────────────
_RESUME_SYSTEM = (
    "You are an expert resume writer and ATS optimization specialist. "
    "You output only valid LaTeX code — no commentary, no markdown code block fences (like ```latex or ```)."
)

_RESUME_PROMPT = """Rewrite the provided LaTeX resume so these keywords are NATURALLY integrated into the WORK EXPERIENCE bullet points.
Do NOT fabricate experience. Preserve all facts (companies, dates, degrees, roles).
Fix any verb tense inconsistencies — use past tense for all bullet points.
Keep the exact LaTeX structure, layout, and formatting as provided in the ORIGINAL RESUME.

For the PROJECTS section, replace the existing projects with the ones provided in RELEVANT PROJECTS. 
Format these new projects identically to how projects are formatted in the ORIGINAL RESUME (with bold titles, tech stacks, and bulleted descriptions). Escape any special LaTeX characters (like % as \\%).

KEYWORDS TO INCORPORATE:
Technical: {required_skills}
Soft: {soft_skills}

RELEVANT PROJECTS:
{relevant_projects_text}

ORIGINAL RESUME (LaTeX):
{resume_text}"""


# ── Cover Letter prompt ────────────────────────────────────────────────────────
_COVER_LETTER_SYSTEM = (
    "You are a professional cover letter writer. "
    "You output only valid LaTeX code — no commentary, no markdown code block fences (like ```latex or ```)."
)

_COVER_LETTER_PROMPT = """Write a tailored cover letter in LaTeX format for:
- Applicant: {name}
- Role: {job_title} at {company_name}

Rules:
1. Exactly 4 body paragraphs — no bullet lists in the body.
2. Integrate these keywords naturally (do NOT just list them): {required_skills}
3. Sound human and specific — avoid clichés like "I am uniquely positioned", "I thrive in environments", "passionate".
4. MENTION AT LEAST ONE RELEVANT PROJECT FROM THE RELEVANT PROJECTS LIST. Include its GitHub link.
5. Use the provided BASE COVER LETTER (LaTeX) as a template. Maintain all its LaTeX formatting and commands (like \\documentclass, \\begin{{document}}, \\end{{document}}, etc.), but REPLACE the body text with your tailored content. Ensure you escape any special LaTeX characters (like % as \\%).

RELEVANT PROJECTS:
{relevant_projects_text}

JOB DESCRIPTION CONTEXT:
{job_text}

BASE COVER LETTER (LaTeX):
{cover_letter_text}"""


# ── Freelance Proposal prompt ──────────────────────────────────────────────────
_FREELANCE_PROPOSAL_SYSTEM = (
    "You are an expert freelance proposal writer. "
    "You output only valid LaTeX code — no commentary, no markdown code block fences (like ```latex or ```)."
)

_FREELANCE_PROPOSAL_PROMPT = """Write a tailored freelance proposal in LaTeX format for:
- Applicant: {name}

Rules:
1. Exactly 4 body paragraphs — no bullet lists in the body.
2. Integrate these keywords naturally (do NOT just list them): {required_skills}
3. Sound human and specific — avoid clichés.
4. Paragraph 4 must focus on WHY the applicant is a strong fit for THIS specific project — concrete matching skills, relevant past work, and a clear call to action.
5. MENTION AT LEAST ONE RELEVANT PROJECT FROM THE RELEVANT PROJECTS LIST. Include its GitHub link.
6. Do NOT mention company culture, company values, or why the company is exciting.
7. Use the provided BASE FREELANCE PROPOSAL (LaTeX) as a template. Maintain all its LaTeX formatting and commands (like \\documentclass, \\begin{{document}}, \\end{{document}}, etc.), but REPLACE the body text with your tailored content. Ensure you escape any special LaTeX characters (like % as \\%).

RELEVANT PROJECTS:
{relevant_projects_text}

PROJECT DESCRIPTION:
{job_text}

BASE FREELANCE PROPOSAL (LaTeX):
{proposal_text}"""


def _get_github_projects_text() -> str:
    """Read the my_github_projects.md file."""
    path = os.path.join(os.path.dirname(__file__), "my_github_projects.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {path}: {e}")
        return ""

def _clean_latex_output(text: str) -> str:
    """Remove markdown code block backticks if the LLM includes them."""
    text = text.strip()
    if text.startswith("```latex"):
        text = text[8:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def select_relevant_projects(keywords: dict, job_text: str, config: dict) -> str:
    """
    Query the LLM to select the most relevant projects based on keywords and job description.
    """
    github_projects_text = _get_github_projects_text()
    if not github_projects_text:
        return ""
        
    prompt = _PROJECT_SELECTION_PROMPT.format(
        required_skills=", ".join(keywords.get("required_skills", [])),
        soft_skills=", ".join(keywords.get("soft_skills", [])),
        job_text=job_text[:4000],
        github_projects_text=github_projects_text[:8000]
    )
    
    if config.get("use_local", True):
        raw = _call_ollama(prompt, _PROJECT_SELECTION_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
        
    return raw.strip()


def generate_resume(resume_text: str, config: dict, keywords: dict, relevant_projects_text: str) -> str:
    """
    Generate a tailored resume as a LaTeX string.

    Args:
        resume_text:            Text extracted from the base resume .tex file.
        config:                 Full config dict.
        keywords:               Extracted keywords dict from keyword_extractor.
        relevant_projects_text: Pre-selected projects markdown string.

    Returns:
        Tailored resume in LaTeX format.
    """
    prompt = _RESUME_PROMPT.format(
        required_skills=", ".join(keywords.get("required_skills", [])),
        soft_skills=", ".join(keywords.get("soft_skills", [])),
        relevant_projects_text=relevant_projects_text,
        resume_text=resume_text,
    )

    if config.get("use_local", True):
        raw = _call_ollama(prompt, _RESUME_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
    
    return _clean_latex_output(raw)


def generate_cover_letter(cover_letter_text: str, config: dict, keywords: dict, job_text: str, relevant_projects_text: str) -> str:
    """
    Generate a tailored cover letter as a LaTeX string.

    Args:
        cover_letter_text:      Text extracted from the base cover letter .tex file.
        config:                 Full config dict.
        keywords:               Extracted keywords dict.
        job_text:               Raw scraped or inline job description.
        relevant_projects_text: Pre-selected projects markdown string.

    Returns:
        Tailored cover letter in LaTeX format.
    """
    personal = config["personal"]
    company_name = keywords.get("company_name") or "the company"
    job_title = keywords.get("job_title") or "the position"

    prompt = _COVER_LETTER_PROMPT.format(
        name=personal["name"],
        job_title=job_title,
        company_name=company_name,
        required_skills=", ".join(keywords.get("required_skills", [])),
        relevant_projects_text=relevant_projects_text,
        job_text=job_text[:4000],
        cover_letter_text=cover_letter_text,
    )

    if config.get("use_local", True):
        raw = _call_ollama(prompt, _COVER_LETTER_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
        
    return _clean_latex_output(raw)


def generate_freelance_proposal(proposal_text: str, config: dict, keywords: dict, job_text: str, relevant_projects_text: str) -> str:
    """
    Generate a tailored freelance proposal as a LaTeX string.

    Args:
        proposal_text:          Text extracted from the base freelance proposal .tex file.
        config:                 Full config dict.
        keywords:               Extracted keywords dict.
        job_text:               Raw scraped or inline job description.
        relevant_projects_text: Pre-selected projects markdown string.

    Returns:
        Tailored freelance proposal in LaTeX format.
    """
    personal = config["personal"]

    prompt = _FREELANCE_PROPOSAL_PROMPT.format(
        name=personal["name"],
        required_skills=", ".join(keywords.get("required_skills", [])),
        relevant_projects_text=relevant_projects_text,
        job_text=job_text[:4000],
        proposal_text=proposal_text,
    )

    if config.get("use_local", True):
        raw = _call_ollama(prompt, _FREELANCE_PROPOSAL_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
        
    return _clean_latex_output(raw)
