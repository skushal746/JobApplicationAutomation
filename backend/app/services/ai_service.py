from .ollama_client import generate as ollama_generate

PROPOSAL_PROMPT_TEMPLATE = """You are an expert freelance proposal writer. 
Write a highly targeted proposal for the following job posting.

STRICT RULES:
1. Do NOT include the date anywhere in the cover letter/proposal.
2. Do NOT add citations for any reason.
3. Be professional, concise, and focus on the client's needs and how I can solve them.

JOB TITLE: {title}
JOB DESCRIPTION: {description}
REQUIRED SKILLS: {skills}

Write the proposal now:"""

def generate_proposal(title: str, description: str, skills: str) -> str:
    return ollama_generate(
        system="You are a professional freelance proposal writer.",
        prompt=PROPOSAL_PROMPT_TEMPLATE.format(
            title=title, 
            description=description, 
            skills=skills
        ),
        model="llama3.2"
    )
