from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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
            job_status=job_data.job_status,
            job_title=job_data.job_title,
            company_name=job_data.company_name,
            location=job_data.location,
            salary_range=job_data.salary_range
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
        db_job_data.job_title = job_data.job_title
        db_job_data.company_name = job_data.company_name
        db_job_data.location = job_data.location
        db_job_data.salary_range = job_data.salary_range
        
        self.db.commit()
        self.db.refresh(db_job_data)
        return db_job_data

    def delete_job_data(self, db_job_data: JobData):
        self.db.delete(db_job_data)
        self.db.commit()

    def get_job_stats(self):
        # 1. Total count
        total = self.db.query(func.count(JobData.id)).scalar() or 0
        
        # 2. Status counts
        status_results = self.db.query(JobData.job_status, func.count(JobData.id)).group_by(JobData.job_status).all()
        status_counts = {status.value: count for status, count in status_results}
        
        # 3. Portal counts
        portal_results = self.db.query(JobData.job_portal_type, func.count(JobData.id)).group_by(JobData.job_portal_type).all()
        portal_counts = {portal.value: count for portal, count in portal_results}
        
        # 4. Daily applications (last 14 days)
        daily_results = self.db.query(
            func.date(JobData.applied_at).label('date'), 
            func.count(JobData.id)
        ).group_by(func.date(JobData.applied_at)).order_by(func.date(JobData.applied_at).desc()).limit(14).all()
        
        daily_applications = [{"date": str(res[0]), "count": res[1]} for res in daily_results]
        
        return {
            "total_applications": total,
            "status_counts": status_counts,
            "portal_counts": portal_counts,
            "daily_applications": daily_applications
        }

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
