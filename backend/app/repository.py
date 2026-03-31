from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import JobData, FormResponse, JobStatus
from .schemas import JobDataCreate, FormResponseCreate

class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_job_data(self):
        return self.db.query(JobData).all()

    def create_job_data(self, job_data: JobDataCreate):
        db_job_data = JobData(
            job_portal_type=job_data.job_portal_type, 
            job_url=job_data.job_url,
            job_status=job_data.job_status
        )
        self.db.add(db_job_data)
        self.db.commit()
        self.db.refresh(db_job_data)
        return db_job_data

    def get_job_data_by_id(self, job_id: int):
        return self.db.query(JobData).filter(JobData.id == job_id).first()

    def update_job_data(self, db_job_data: JobData, job_data: JobDataCreate):
        db_job_data.job_portal_type = job_data.job_portal_type
        db_job_data.job_url = job_data.job_url
        db_job_data.job_status = job_data.job_status
        self.db.commit()
        self.db.refresh(db_job_data)
        return db_job_data

    def delete_job_data(self, db_job_data: JobData):
        self.db.delete(db_job_data)
        self.db.commit()

    # FormResponse Methods
    def get_form_response_by_question(self, question_text: str):
        return self.db.query(FormResponse).filter(FormResponse.question_text == question_text).first()

    def create_form_response(self, form_response: FormResponseCreate):
        db_form_response = FormResponse(
            question_text=form_response.question_text,
            answer_text=form_response.answer_text
        )
        self.db.add(db_form_response)
        self.db.commit()
        self.db.refresh(db_form_response)
        return db_form_response

def get_repository(db: Session = Depends(get_db)):
    return Repository(db)
