from fastapi import Depends
from .repository import Repository, get_repository
from .automation_service import LinkedInAutomation

class Service:
    def __init__(self, repository: Repository, automation: LinkedInAutomation):
        self.repository = repository
        self.automation = automation

    def get_job_data(self):
        return self.repository.get_all_job_data()

    def create_job_data(self, job_data):
        return self.repository.create_job_data(job_data)

    def update_job_data(self, job_id, job_data):
        db_job_data = self.repository.get_job_data_by_id(job_id)
        if not db_job_data:
            return None
        return self.repository.update_job_data(db_job_data, job_data)

    async def automate_linkedin(self, job_id: int):
        return await self.automation.automate_job(job_id)

    async def automate_all_linkedin(self):
        jobs = self.repository.get_all_job_data()
        count = 0
        for job in jobs:
            if job.job_portal_type == "linkedin" and job.job_status == "active":
                # We can run these in sequence or background tasks
                asyncio.create_task(self.automation.automate_job(job.id))
                count += 1
        return count

    def get_job_data_by_id(self, job_id):
        return self.repository.get_job_data_by_id(job_id)

    def delete_job_data(self, job_id):
        db_job_data = self.repository.get_job_data_by_id(job_id)
        if not db_job_data:
            return False
        self.repository.delete_job_data(db_job_data)
        return True

def get_service(repository: Repository = Depends(get_repository)):
    automation = LinkedInAutomation(repository)
    return Service(repository, automation)
