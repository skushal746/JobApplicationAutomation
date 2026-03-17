"""
document_generator.py

Generates tailored resume and cover letter as Markdown strings.
"""

from utils.github import get_github_repos, format_repos_for_llm
from projects_config import PROJECTS_BY_ROLE, DEFAULT_PROJECTS
from utils.ai import _call_ollama, _call_gemini



# ── Resume prompt ──────────────────────────────────────────────────────────────
_RESUME_SYSTEM = (
    "You are an expert resume writer and ATS optimization specialist. "
    "You output only clean Markdown — no commentary, no preamble, no fences."
)

_RESUME_PROMPT = """Rewrite the resume below so these keywords are NATURALLY integrated.
Do NOT fabricate experience. Preserve all facts (companies, dates, degrees, roles).
Fix any verb tense inconsistencies — use past tense for all bullet points.
Reduce bolding — only bold company names and job titles, not every keyword.
Output clean Markdown with these sections in order:
# {name}
{email} | {phone} | {linkedin} | {github}

---

## PROFESSIONAL SUMMARY
(2-3 sentences)

---

## TECHNICAL SKILLS
(bullet list)

---

## WORK EXPERIENCE

### Role | Company | Location
#### Start – End
- bullet
- bullet

(repeat for each role)

---

## EDUCATION
(one line per degree)

---

KEYWORDS TO INCORPORATE:
Technical: {required_skills}
Soft: {soft_skills}

ORIGINAL RESUME:
{resume_text}"""


# ── Cover Letter prompt ────────────────────────────────────────────────────────
_COVER_LETTER_SYSTEM = (
    "You are a professional cover letter writer. "
    "You output only clean Markdown — no commentary, no preamble, no fences."
)

_COVER_LETTER_PROMPT = """Write a cover letter for:
- Applicant: {name}
- Role: {job_title} at {company_name}

Rules:
1. Exactly 4 body paragraphs — no bullet lists in the body
2. Integrate these keywords naturally (do NOT just list them): {required_skills}
3. Sound human and specific — avoid clichés like "I am uniquely positioned", "I thrive in environments", "passionate"
4. Minimal bolding — only the applicant name in the header
5. MENTION AT LEAST ONE RELEVANT PROJECT FROM THE LIST BELOW. Include its GitHub link (if provided) and highlight how it relates to the role's requirements.
6. Use the list of all GitHub repositories provided to find other relevant projects if the specific projects list doesn't have a perfect match.
7. Output clean Markdown in this structure:

# {name}
{email} | {phone} | {linkedin} | {github_url}

---

Dear Hiring Manager,

[paragraph 1 — who you are, your strongest credential, why this role specifically]

[paragraph 2 — most relevant accomplishment with a specific metric from experience. If you mention a project, include its GitHub link.]

[paragraph 3 — continuation of most relevant accomplishment or another key project. Focus on technical depth.]

[paragraph 4 — why this company specifically, forward-looking, call to action]

Sincerely,
**{name}**

RELEVANT PROJECTS FOR THIS ROLE:
{relevant_projects}

ALL GITHUB REPOSITORIES:
{github_repos_list}

JOB DESCRIPTION CONTEXT:
{job_text}

APPLICANT'S BASE COVER LETTER (use for tone and factual reference only):
{cover_letter_text}"""



# ── Freelance Cover Letter prompt (for inline job_descriptions) ────────────────
_FREELANCE_COVER_LETTER_PROMPT = """Write a freelance proposal / cover letter for:
- Applicant: {name}

Rules:
1. Exactly 4 body paragraphs — no bullet lists in the body
2. Integrate these keywords naturally (do NOT just list them): {required_skills}
3. Sound human and specific — avoid clichés like "I am uniquely positioned", "I thrive in environments", "passionate"
4. Minimal bolding — only the applicant name in the header
5. Paragraph 4 must focus on WHY the applicant is a strong fit for THIS specific project —
   concrete matching skills, relevant past work, and a clear call to action.
6. MENTION AT LEAST ONE RELEVANT PROJECT FROM THE LIST BELOW. Include its GitHub link (if provided).
7. Use the list of all GitHub repositories provided to find other relevant projects if needed.
8. Do NOT mention company culture, company values, or why the company is exciting.
9. Output clean Markdown in this structure:

# {name}
{email} | {phone} | {linkedin} | {github_url}

---

Hello,

[paragraph 1 — who you are, your strongest credential for this type of project]

[paragraph 2 — most relevant accomplishment or project with a specific metric matching the project needs. Link to the code if possible.]

[paragraph 3 — continuation: another relevant accomplishment or technical depth that addresses the project.]

[paragraph 4 — why you specifically are the right fit for THIS project: concrete skill match, relevant experience,
and a clear call to action inviting the client to discuss further]

Best regards,
**{name}**

RELEVANT PROJECTS FOR THIS ROLE:
{relevant_projects}

ALL GITHUB REPOSITORIES:
{github_repos_list}

JOB DESCRIPTION:
{job_text}

APPLICANT'S BASE COVER LETTER (use for tone and factual reference only):
{cover_letter_text}"""



def _deduplicate(text: str, end_marker: str) -> str:
    """
    Local LLMs sometimes repeat their output multiple times.
    Find the first natural end of the document (end_marker) and
    strip everything after it, keeping only the first copy.

    Args:
        text:       Raw model output.
        end_marker: String that marks the end of one complete document
                    (e.g. 'Sincerely,' for cover letters, '## EDUCATION' for resumes).
    Returns:
        Trimmed string containing only the first complete document.
    """
    idx = text.find(end_marker)
    if idx == -1:
        return text.strip()  # marker not found — return as-is

    # Include the marker line itself plus a couple of lines after it
    end = text.find("\n", idx + len(end_marker))
    # advance one more newline to capture the name line below "Sincerely,"
    if end != -1:
        end = text.find("\n", end + 1)
    return text[: end if end != -1 else None].strip()

def generate_resume(resume_text: str, config: dict, keywords: dict) -> str:
    """
    Generate a tailored resume as a Markdown string.

    Args:
        resume_text: Text extracted from the base resume PDF.
        config:      Full config dict.
        keywords:    Extracted keywords dict from keyword_extractor.

    Returns:
        Tailored resume in Markdown format.
    """
    personal = config["personal"]
    prompt = _RESUME_PROMPT.format(
        name=personal["name"],
        email=personal.get("email", ""),
        phone=personal.get("phone", ""),
        linkedin=personal.get("linkedin", ""),
        github=personal.get("github", ""),
        required_skills=", ".join(keywords.get("required_skills", [])),
        soft_skills=", ".join(keywords.get("soft_skills", [])),
        resume_text=resume_text[:6000],
    )

    if config.get("use_local", True):
        raw = _call_ollama(prompt, _RESUME_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
    return _deduplicate(raw, "## EDUCATION")


def generate_cover_letter(
    cover_letter_text: str,
    config: dict,
    keywords: dict,
    job_text: str,
    freelance: bool = False,
) -> str:
    """
    Generate a tailored cover letter as a Markdown string.

    Args:
        cover_letter_text: Text extracted from the base cover letter PDF.
        config:            Full config dict.
        keywords:          Extracted keywords dict.
        job_text:          Raw scraped or inline job description.
        freelance:         If True, uses the freelance template (no company paragraph).

    Returns:
        Tailored cover letter in Markdown format.
    """
    personal = config["personal"]
    company_name = keywords.get("company_name") or "the company"
    job_title = keywords.get("job_title") or "the position"
    github_user = personal.get("github", "")

    # 1. Fetch GitHub Repos
    repos = get_github_repos(github_user)
    github_repos_list = format_repos_for_llm(repos)
    github_base = "github.com/" + github_user.split("github.com/")[-1].strip("/") if github_user else ""

    # 2. Pick relevant curated projects
    relevant_curated = []
    # Search for job title in PROJECTS_BY_ROLE keys
    matched_role = None
    for role in PROJECTS_BY_ROLE.keys():
        if role.lower() in job_title.lower() or job_title.lower() in role.lower():
            matched_role = role
            break
    
    if matched_role:
        curated_list = PROJECTS_BY_ROLE[matched_role]
    else:
        curated_list = DEFAULT_PROJECTS
        
    for p in curated_list:
        repo_link = f"https://{github_base}/{p['github_repo']}" if github_base and p.get('github_repo') else ""
        relevant_curated.append(f"- PROJECT: {p['name']}\n  TECH: {p['tech_stack']}\n  DESC: {p['description']}\n  LINK: {repo_link}")
    
    relevant_projects_str = "\n".join(relevant_curated)

    if freelance:
        prompt = _FREELANCE_COVER_LETTER_PROMPT.format(
            name=personal["name"],
            email=personal.get("email", ""),
            phone=personal.get("phone", ""),
            linkedin=personal.get("linkedin", ""),
            github_url=github_base,
            required_skills=", ".join(keywords.get("required_skills", [])),
            job_text=job_text[:4000],
            cover_letter_text=cover_letter_text[:3000],
            relevant_projects=relevant_projects_str,
            github_repos_list=github_repos_list
        )
    else:
        prompt = _COVER_LETTER_PROMPT.format(
            name=personal["name"],
            email=personal.get("email", ""),
            phone=personal.get("phone", ""),
            linkedin=personal.get("linkedin", ""),
            github_url=github_base,
            job_title=job_title,
            company_name=company_name,
            required_skills=", ".join(keywords.get("required_skills", [])),
            job_text=job_text[:4000],
            cover_letter_text=cover_letter_text[:3000],
            relevant_projects=relevant_projects_str,
            github_repos_list=github_repos_list
        )

    if config.get("use_local", True):
        raw = _call_ollama(prompt, _COVER_LETTER_SYSTEM, config)
    else:
        raw = _call_gemini(prompt, config)
    return _deduplicate(raw, "Sincerely," if not freelance else "Best regards,")

