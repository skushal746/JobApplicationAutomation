"""
document_generator.py

Generates tailored resume, cover letter, and freelance proposal as LaTeX strings.
"""

import os
from utils.ai import _call_ollama, _call_gemini, _call_openai


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

_FREELANCE_PROPOSAL_PROMPT = """Write a comprehensive, tailored freelance proposal in LaTeX format for:
- Applicant: {name}

CRITICAL FORMATTING RULES:
1. The final document MUST be exactly 3 pages long when compiled. Expand every section to be highly descriptive and detailed enough to fill 3 full pages.
2. Use the BASE FREELANCE PROPOSAL (LaTeX) as the structural template. Keep ALL LaTeX preamble, packages, and formatting commands exactly as-is. Only replace the body content.
3. Escape all special LaTeX characters (e.g., % → \\%, & → \\&, # → \\#, _ → \\_).
4. Do NOT use markdown code fences (no ```latex).
5. UPWORK POLICY — DO NOT include phone numbers, email addresses, Skype IDs, WhatsApp numbers, or any direct calling/messaging contact details anywhere in the document. GitHub links and LinkedIn profile URLs are permitted.

CONTENT RULES — generate ALL 5 of the following sections inside \\begin{{document}}...\\end{{document}}:

SECTION 1 — OPENING (2 paragraphs):
- Paragraph 1: Strong, specific introduction tailored to this exact project. Reference the job's specific requirements using these keywords naturally: {required_skills}.
- Paragraph 2: Summarise years of experience, key technologies, and industries served. Draw facts ONLY from the RESUME provided below — do not invent roles or dates.

SECTION 2 — WHY I'M A STRONG FIT (titled: "Why I'm a Strong Fit"):
- Minimum 6 descriptive bullet points.
- Each bullet must start with a bold keyword label (e.g., \\textbf{{Microservices Architecture:}}).
- Each bullet must be 2-3 sentences long. Ground every claim in real experience taken from the RESUME (companies, tools, outcomes mentioned there).
- Directly map each bullet to a required skill from: {required_skills}.

SECTION 3 — RELEVANT GITHUB PROJECTS (titled: "Relevant GitHub Projects"):
- List EXACTLY 4 projects chosen from RELEVANT PROJECTS below — pick those most aligned to the job keywords.
- For EACH project use this exact LaTeX structure:
    \\textbf{{Project Name -- Brief Subtitle}}\\\\
    \\href{{GITHUB_URL}}{{\\texttt{{github.com/skushal746/ProjectName}}}} \\hfill \\textit{{Tech1, Tech2, Tech3}}
    \\begin{{itemize}}...\\end{{itemize}}
- Each project must have 3-4 bullet points (1-2 sentences each) explaining what was built, what problem it solved, and which keywords it demonstrates.
- ALWAYS use the real GitHub URL from the RELEVANT PROJECTS list as a clickable \\href link. Never fabricate URLs.

SECTION 4 — HOW I WORK (titled: "How I Approach Freelance Engagements"):
- Minimum 5 bullet points, each starting with a bold label.
- Each bullet 2-3 sentences covering: discovery, incremental delivery, async communication, code quality, timezone availability, and handoff-ready deliverables.

SECTION 5 — CLOSING (titled: "How I Can Help on This Project" then "Next Steps"):
- "How I Can Help" subsection: 5 specific bullet points tied to the project's exact stated requirements.
- "Next Steps" paragraph (2-3 sentences): invite a discovery call, include clickable links to GitHub (\\href{{https://github.com/skushal746}}{{github.com/skushal746}}) and LinkedIn (\\href{{https://www.linkedin.com/in/skushal746}}{{linkedin.com/in/skushal746}}).
- Closing sign-off with name, email, and phone.

RELEVANT GITHUB PROJECTS (with URLs — use these exact URLs in the document):
{relevant_projects_text}

MY RESUME (use this as the single source of truth for experience, roles, and dates):
{resume_text}

PROJECT / JOB DESCRIPTION:
{job_text}

BASE FREELANCE PROPOSAL (LaTeX) — preserve preamble, replace body only:
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
    """Robustly extract a valid LaTeX document from LLM output.

    LLMs often surround LaTeX with prose, review comments, or markdown fences.
    This function anchors extraction to \\documentclass ... \\end{document},
    which are always present in a valid standalone LaTeX file. Any text before
    \\documentclass or after \\end{document} is discarded.

    Also strips packages known to break on modern TeX Live (2021+).
    """
    import re

    # ── Step 1: extract just the LaTeX document by its anchors ──────────────
    # Match from \documentclass to \end{document} (inclusive), spanning newlines.
    match = re.search(
        r"(\\documentclass\b.*?\\end\{document\})",
        text,
        re.DOTALL,
    )
    if match:
        text = match.group(1)
    else:
        # Fallback: strip markdown fences manually if anchors not found
        text = text.strip()
        if text.startswith("```latex"):
            text = text[8:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

    # ── Step 2: remove packages that break on TeX Live 2021+ ────────────────
    # inputenc with utf8 is a no-op on modern TeX Live and causes a fatal error.
    text = re.sub(r"\\usepackage\[[^\]]*utf[^\]]*\]\{inputenc\}\s*\n?", "", text)

    # ── Step 3: remove any invalid \hyperseturlstyle command LLMs sometimes add
    text = re.sub(r"\\hyperseturlstyle\{[^}]*\}\s*\n?", "", text)

    # ── Step 4: Upwork compliance — remove phone numbers and email addresses ────
    # GitHub links and LinkedIn URLs are allowed.
    # Remove phone number patterns (various formats)
    text = re.sub(r"(\+?\d[\d\s\-\(\)]{7,}\d)[^\n]*", "", text)
    # Remove email addresses
    text = re.sub(r"[^\s{{}}\\]+@[^\s{{}}\\]+\.[a-zA-Z]{{2,}}", "", text)

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
        github_projects_text=github_projects_text[:15000]
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


def generate_freelance_proposal(proposal_text: str, config: dict, keywords: dict, job_text: str, relevant_projects_text: str, resume_text: str = "") -> str:
    """
    Generate a tailored freelance proposal as a LaTeX string.

    Args:
        proposal_text:          Text extracted from the base freelance proposal .tex file.
        config:                 Full config dict.
        keywords:               Extracted keywords dict.
        job_text:               Raw scraped or inline job description.
        relevant_projects_text: Pre-selected projects markdown string (with GitHub URLs).
        resume_text:            LaTeX source of the applicant's resume (used as source of truth
                                for experience, roles, and dates).

    Returns:
        Tailored freelance proposal in LaTeX format (target: 3 pages).
    """
    personal = config["personal"]

    prompt = _FREELANCE_PROPOSAL_PROMPT.format(
        name=personal["name"],
        required_skills=", ".join(keywords.get("required_skills", [])),
        relevant_projects_text=relevant_projects_text,
        resume_text=resume_text[:6000],   # ~6k chars covers a full LaTeX resume
        job_text=job_text[:4000],
        proposal_text=proposal_text,
    )

    # Proposals require strict LaTeX output — prefer a stronger cloud model.
    # Set proposal_use_openai: true in config to use OpenAI (recommended).
    # Set proposal_use_gemini: true to use Gemini instead.
    # Falls back to local Ollama only if neither flag is set.
    use_openai = (
        not config.get("use_local", True)
        or config.get("proposal_use_openai", False)
    )
    use_gemini = (
        not use_openai
        and (not config.get("use_local", True) or config.get("proposal_use_gemini", False))
    )

    if use_openai:
        raw = _call_openai(prompt, _FREELANCE_PROPOSAL_SYSTEM, config)
    elif use_gemini:
        raw = _call_gemini(prompt, config)
    else:
        raw = _call_ollama(prompt, _FREELANCE_PROPOSAL_SYSTEM, config)

    return _clean_latex_output(raw)
