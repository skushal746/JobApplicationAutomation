import asyncio
import os
import httpx
from .repository import Repository
from .utils.config_loader import get_user_context_string
from .models import JobStatus, JobPortalType, JobApplication
from .schemas import QuestionAnswerCreate
from .scripts.linkedin import LinkedInStrategy
from .scripts.workday import WorkdayStrategy

class AutomationService:
    def __init__(self, repository: Repository):
        self.repository = repository
        self.browser_url = os.getenv("BROWSER_WS", "ws://browser:3000?token=secret_token")
        self.ollama_base = os.getenv("OLLAMA_BASE", "http://localhost:11434")
        
        # Initialize strategies with browser config
        self.strategies = {
            JobPortalType.linkedin: LinkedInStrategy(self.browser_url),
            JobPortalType.workday: WorkdayStrategy(self.browser_url)
        }

    async def run_automation(self, job_app_id: int):
        job_app = self.repository.get_application_by_id(job_app_id)
        if not job_app: 
            print(f"Application {job_app_id} not found")
            return False
        
        company = job_app.company
        portal_type = company.portal_type
        strategy = self.strategies.get(portal_type)
        
        if not strategy:
            print(f"No strategy found for {portal_type}")
            return False

        # --- Data Preparation ---
        # 1. Credentials
        credentials = {
            "username": company.username,
            "password": company.password
        }

        # 2. Resumes
        resume_locations = [r.location for r in job_app.resumes]

        # 3. Knowledge Callback (get_answer)
        async def get_answer_callback(question_text: str) -> str:
            # Check DB
            qa = self.repository.get_qa_by_company_and_question(company.id, question_text)
            if qa:
                return qa.answer_text
            
            # Fallback to LLM
            answer = await self._get_llm_answer(question_text)
            
            # Save for future
            self.repository.create_qa(QuestionAnswerCreate(
                company_id=company.id,
                question_text=question_text,
                answer_text=answer
            ))
            return answer

        # --- Execution ---
        # Note: job_url is currently missing from the model. 
        # Using domain as a placeholder or passing empty if not applicable.
        # This will likely need the job_url added back to the request or model.
        job_url = getattr(job_app, "job_url", company.domain) 

        print(f"Starting automation for {company.name} using {portal_type.value} strategy...")
        
        success = False
        if portal_type == JobPortalType.linkedin:
            success = await strategy.execute(
                job_url=job_url,
                company_id=company.id,
                get_answer=get_answer_callback
            )
        elif portal_type == JobPortalType.workday:
            success = await strategy.execute(
                job_url=job_url,
                company_id=company.id,
                get_answer=get_answer_callback,
                credentials=credentials,
                resume_locations=resume_locations
            )

        if success:
            self.repository.update_application_status(job_app, JobStatus.applied)
            print(f"Successfully applied to {company.name}")
        else:
            print(f"Automation failed for {company.name}")
            
        return success

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
