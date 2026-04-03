import asyncio
import os
import httpx
from playwright.async_api import async_playwright
from .repository import Repository
from .utils.config_loader import get_user_context_string
from .schemas import FormResponseCreate, JobDataCreate
from .models import JobStatus, JobPortalType

class LinkedInAutomation:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.browser_url = os.getenv("BROWSER_WS", "ws://browser:3000?token=secret_token")
        self.ollama_base = os.getenv("OLLAMA_BASE", "http://localhost:11434")

    async def automate_job(self, job_id: int):
        job = self.repository.get_job_data_by_id(job_id)
        if not job or job.job_portal_type != JobPortalType.linkedin:
            return False

        async with async_playwright() as p:
            try:
                # Connect to the remote browserless service
                browser = await p.chromium.connect_over_cdp(self.browser_url)
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to the job URL
                await page.goto(job.job_url, wait_until="networkidle")

                # Look for "Easy Apply" button
                easy_apply_button = page.locator("button:has-text('Easy Apply')").first
                if await easy_apply_button.count() == 0:
                    print(f"Easy Apply not found for job {job_id}")
                    return False

                await easy_apply_button.click()
                await asyncio.sleep(2)

                # Modal Loop: Keep clicking "Next" or "Review" until "Submit"
                max_steps = 10
                for _ in range(max_steps):
                    # Check for questions in the current step
                    await self._handle_form_questions(page)

                    # Click Next/Review/Submit
                    next_button = page.locator("button:has-text('Next'), button:has-text('Review'), button:has-text('Submit application')").first
                    if await next_button.count() == 0:
                        break
                    
                    button_text = await next_button.inner_text()
                    await next_button.click()
                    await asyncio.sleep(1)

                    if "Submit application" in button_text:
                        # Update status to applied
                        self.repository.update_job_data(job, JobDataCreate(
                            job_portal_type=job.job_portal_type,
                            job_url=job.job_url,
                            job_status=JobStatus.applied
                        ))
                        break

                await browser.close()
                return True

            except Exception as e:
                print(f"Error automating job {job_id}: {e}")
                return False

    async def _handle_form_questions(self, page):
        """Detects questions in the current modal and fills them using DB or LLM."""
        # Find all labels or fieldsets that look like questions
        questions = page.locator(".jobs-easy-apply-form-section__grouping")
        count = await questions.count()

        for i in range(count):
            section = questions.nth(i)
            label = section.locator("label").first
            if await label.count() == 0:
                continue

            question_text = (await label.inner_text()).strip()
            
            # 1. Check DB first
            db_response = self.repository.get_form_response_by_question(question_text)
            if db_response:
                answer = db_response.answer_text
            else:
                # 2. Call Ollama LLM
                answer = await self._get_llm_answer(question_text)
                # 3. Store in DB
                self.repository.create_form_response(FormResponseCreate(
                    question_text=question_text,
                    answer_text=answer
                ))

            # Fill the input (handle text, choice, etc.)
            input_field = section.locator("input[type='text'], textarea, select").first
            if await input_field.count() > 0:
                tag_name = await input_field.evaluate("el => el.tagName")
                if tag_name == "SELECT":
                    await input_field.select_option(label=answer)
                else:
                    await input_field.fill(answer)

    async def _get_llm_answer(self, question):
        """Calls the local Ollama LLM to generate an answer for a specific question."""
        user_context = get_user_context_string()
        prompt = f"""
        You are an AI assistant helping a job applicant.
        Below is the applicant's profile for context:
        {user_context}

        Answer the following job application question based on the applicant's background. 
        If the question is about personal details (phone, email, name), use the provided context.
        Keep the answer concise and professional.

        Question: {question}
        Answer:
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base}/api/generate",
                    json={
                        "model": "llama3", # or whichever model is set up
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json().get("response", "Yes").strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Yes" # Default fallback
        return "Yes"
