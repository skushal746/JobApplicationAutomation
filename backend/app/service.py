from fastapi import Depends
from .repository import Repository, get_repository

class Service:
    def __init__(self, repository: Repository):
        self.repository = repository

    def get_job_data(self):
        return self.repository.get_all_job_data()

    def create_job_data(self, job_data):
        return self.repository.create_job_data(job_data)

    def update_job_data(self, job_id, job_data):
        db_job_data = self.repository.get_job_data_by_id(job_id)
        if not db_job_data:
            return None
        return self.repository.update_job_data(db_job_data, job_data)

    def get_job_data_by_id(self, job_id):
        return self.repository.get_job_data_by_id(job_id)

    def delete_job_data(self, job_id):
        db_job_data = self.repository.get_job_data_by_id(job_id)
        if not db_job_data:
            return False
        self.repository.delete_job_data(db_job_data)
        return True

def get_service(repository: Repository = Depends(get_repository)):
    return Service(repository)
