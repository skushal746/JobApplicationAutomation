import asyncio
from fastapi import Depends
from .repository import Repository, get_repository
from .automation_service import AutomationService
from .schemas import CompanyCreate, QuestionAnswerCreate, JobApplicationCreate
from .models import JobStatus

class Service:
    def __init__(self, repository: Repository, automation: AutomationService):
        self.repository = repository
        self.automation = automation

    # --- Company ---
    def get_companies(self):
        return self.repository.get_all_companies()

    def create_company(self, company: CompanyCreate):
        return self.repository.create_company(company)

    def get_company(self, company_id: int):
        return self.repository.get_company_by_id(company_id)

    # --- QuestionAnswer ---
    def create_qa(self, qa: QuestionAnswerCreate):
        return self.repository.create_qa(qa)

    # --- JobApplication ---
    def get_applications(self):
        return self.repository.get_all_applications()

    def create_application(self, app: JobApplicationCreate):
        return self.repository.create_application(app)

    def get_application(self, app_id: int):
        return self.repository.get_application_by_id(app_id)

    def get_job_stats(self):
        return self.repository.get_job_stats()

    async def trigger_automation(self, job_app_id: int):
        # This will be called via BackgroundTasks in the controller
        return await self.automation.run_automation(job_app_id)

    async def automate_all_pending(self):
        apps = self.repository.get_all_applications()
        count = 0
        for app in apps:
            if app.job_status == JobStatus.active:
                asyncio.create_task(self.automation.run_automation(app.id))
                count += 1
        return count

def get_service(repository: Repository = Depends(get_repository)):
    automation = AutomationService(repository)
    return Service(repository, automation)
