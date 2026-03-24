# Job Application Automation

Automatically tailors your **resume** and **cover letter** to any job listing URL — extracting ATS keywords with Gemini and exporting polished PDFs.

---

## Setup

### 1. Install dependencies
```bash
cd /path/to/JobApplicationAutomation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Add your documents
Place your base PDF documents in the `assets/` folder:
```
assets/
  resume.pdf        ← your current resume
  cover_letter.pdf  ← your base cover letter
```

### 3. Fill in `config.yaml`
```yaml
gemini_api_key: "YOUR_KEY_HERE"   # https://aistudio.google.com (free)

personal:
  name: "Your Name"
  email: "you@example.com"
  phone: "+1-555-000-0000"
  linkedin: "linkedin.com/in/you"
  github: "github.com/you"
  location: "City, State"

assets:
  resume: "assets/resume.pdf"
  cover_letter: "assets/cover_letter.pdf"
```

---

## Usage

```bash
python main.py --url "https://www.linkedin.com/jobs/view/1234567890"
```

Output PDFs are saved to `output/`:
```
output/
  resume.pdf
  cover_letter.pdf
```

You can also specify a custom output directory:
```bash
python main.py --url "https://..." --output ./applications/google
```

---

## Features

- **GitHub Integration**: Automatically fetches your public repositories to showcase live coding projects.
- **Smart Project Matching**: Uses `src/projects_config.py` to select the most relevant projects based on the job role.
- **Freelance Support**: Enhanced templates for part-time and freelance project proposals.
- **Project Constant File**: Easily manage your project descriptions and tech stacks in one place.

---

## How It Works

```
Job URL / Info
  └─→ [Scraper]             – extracts job description text
        └─→ [GitHub Parser] – fetches your live repos & project links
        └─→ [Gemini/Ollama] – identifies ATS keywords & job details
              └─→ [LLM]     – rewrites resume with keywords woven in
              └─→ [LLM]     – writes tailored cover letter with relevant projects & GitHub links
                    └─→ [MD-to-PDF] → resume.pdf + cover_letter.pdf
```

| Module | Purpose |
|---|---|
| `src/scraper.py` | Handles LinkedIn, Indeed, Greenhouse, Lever, Workday & generic pages |
| `src/github_parser.py` | Fetches live repositories from your GitHub profile |
| `src/projects_config.py` | Stores curated project details and tech stacks by role |
| `src/keyword_extractor.py` | Returns required skills, soft skills, job title, company |
| `src/document_generator.py` | Tailors documents while integrating projects and GitHub links |
| `src/pdf_parser.py` | Reads text from your base PDFs |
| `src/convert_md.py` | Converts seasoned Markdown to polished PDF |

---

## Notes

- If a job board blocks scraping (e.g. LinkedIn requires login), paste the job description text directly into a `.txt` file and use `--text-file` as a future fallback.
- Your `config.yaml` contains your API key — consider adding it to `.gitignore` before pushing to a public repo.
