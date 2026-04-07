import asyncio
import os
import httpx
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Page
from .repository import Repository
from .utils.config_loader import get_user_context_string
from .models import JobStatus, JobPortalType, JobApplication, Company
from .schemas import QuestionAnswerCreate

class BaseAutomation(ABC):
    def __init__(self, repository: Repository, browser_url: str, ollama_base: str):
        self.repository = repository
        self.browser_url = browser_url
        self.ollama_base = ollama_base

    @abstractmethod
    async def run(self, job_app: JobApplication):
        pass

    async def _get_answer(self, company_id: int, question_text: str) -> str:
        # 1. Check Company-specific Q&A
        qa = self.repository.get_qa_by_company_and_question(company_id, question_text)
        if qa:
            return qa.answer_text
        
        # 2. Fallback to LLM
        answer = await self._get_llm_answer(question_text)
        
        # 3. Save for future use
        self.repository.create_qa(QuestionAnswerCreate(
            company_id=company_id,
            question_text=question_text,
            answer_text=answer
        ))
        return answer

    async def _get_llm_answer(self, question: str):
        user_context = get_user_context_string()
        prompt = f"""
        You are an AI assistant helping a job applicant.
        Below is the applicant's profile for context:
        {user_context}

        Answer the following job application question based on the applicant's background. 
        Keep the answer concise and professional.

        Question: {question}
        Answer:
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json().get("response", "Yes").strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Yes"
        return "Yes"

class LinkedInStrategy(BaseAutomation):
    async def run(self, job_app: JobApplication):
        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.browser_url)
                context = await browser.new_context()
                page = await context.new_page()
                # job_url removed from model. Replace with derived URL if needed.
                # await page.goto(job_app.job_url, wait_until="networkidle") 

                easy_apply_button = page.locator("button:has-text('Easy Apply')").first
                if await easy_apply_button.count() == 0:
                    return False

                await easy_apply_button.click()
                await asyncio.sleep(2)

                for _ in range(10):
                    await self._handle_form(page, job_app.company_id)
                    next_button = page.locator("button:has-text('Next'), button:has-text('Review'), button:has-text('Submit application')").first
                    if await next_button.count() == 0: break
                    
                    text = await next_button.inner_text()
                    await next_button.click()
                    await asyncio.sleep(1)
                    if "Submit application" in text:
                        self.repository.update_application_status(job_app, JobStatus.applied)
                        break

                await browser.close()
                return True
            except Exception as e:
                print(f"LinkedIn Error: {e}")
                return False

    async def _handle_form(self, page: Page, company_id: int):
        questions = page.locator(".jobs-easy-apply-form-section__grouping")
        for i in range(await questions.count()):
            section = questions.nth(i)
            label = section.locator("label").first
            if await label.count() == 0: continue
            q_text = (await label.inner_text()).strip()
            answer = await self._get_answer(company_id, q_text)
            
            input_field = section.locator("input[type='text'], textarea, select").first
            if await input_field.count() > 0:
                if await input_field.evaluate("el => el.tagName") == "SELECT":
                    await input_field.select_option(label=answer)
                else:
                    await input_field.fill(answer)

class WorkdayStrategy(BaseAutomation):
    async def run(self, job_app: JobApplication):
        company = job_app.company
        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.browser_url)
                context = await browser.new_context()
                page = await context.new_page()
                # job_url removed from model. Replace with derived URL if needed.
                # await page.goto(job_app.job_url, wait_until="networkidle")

                # 1. Start Application - Apply Manually
                apply_button = page.locator("button:has-text('Apply')").first
                await apply_button.click()
                await page.locator("button:has-text('Apply Manually')").click()
                await asyncio.sleep(2)

                # 2. Login if needed
                if "login" in page.url.lower():
                    await page.fill("input[type='email'], input[name='username']", company.username)
                    await page.fill("input[type='password']", company.password)
                    await page.click("button[type='submit'], button:has-text('Sign In')")
                    await asyncio.sleep(3)

                # 3. Form Loop
                max_steps = 8
                for _ in range(max_steps):
                    await self._fill_workday_section(page, company.id)
                    
                    # Upload Logic (Mock)
                    if "resume" in page.url.lower() or await page.locator("input[type='file']").count() > 0:
                        file_input = page.locator("input[type='file']").first
                        if await file_input.count() > 0 and job_app.resumes:
                            await file_input.set_input_files(job_app.resumes[0].location)

                    next_btn = page.locator("button:has-text('Save and Continue'), button:has-text('Submit')").first
                    if await next_btn.count() == 0: break
                    
                    btn_text = await next_btn.inner_text()
                    await next_btn.click()
                    await asyncio.sleep(2)
                    
                    if "Submit" in btn_text:
                        self.repository.update_application_status(job_app, JobStatus.applied)
                        break

                await browser.close()
                return True
            except Exception as e:
                print(f"Workday Error: {e}")
                return False

    async def _fill_workday_section(self, page: Page, company_id: int):
        fields = page.locator("div.css-1") # Simplified selector for WD fields
        # In practice, Workday uses complex structures. 
        # For this design, we iterate over labels and their associated inputs.
        labels = page.locator("label")
        for i in range(await labels.count()):
            label = labels.nth(i)
            q_text = (await label.inner_text()).strip()
            if not q_text: continue
            
            answer = await self._get_answer(company_id, q_text)
            
            # Find associated input by id or aria-labelledby
            input_id = await label.get_attribute("for")
            if input_id:
                input_field = page.locator(f"#{input_id.replace('.', '\\.')}")
                if await input_field.count() > 0:
                    tag = await input_field.evaluate("el => el.tagName")
                    if tag == "SELECT":
                        await input_field.select_option(label=answer)
                    else:
                        await input_field.fill(answer)

class AutomationService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.browser_url = os.getenv("BROWSER_WS", "ws://browser:3000?token=secret_token")
        self.ollama_base = os.getenv("OLLAMA_BASE", "http://localhost:11434")
        self.strategies = {
            JobPortalType.linkedin: LinkedInStrategy(repository, self.browser_url, self.ollama_base),
            JobPortalType.workday: WorkdayStrategy(repository, self.browser_url, self.ollama_base)
        }

    async def run_automation(self, job_app_id: int):
        job_app = self.repository.get_application_by_id(job_app_id)
        if not job_app: return False
        
        portal_type = job_app.company.portal_type
        strategy = self.strategies.get(portal_type)
        
        if not strategy:
            print(f"No strategy found for {portal_type}")
            return False
            
        return await strategy.run(job_app)
