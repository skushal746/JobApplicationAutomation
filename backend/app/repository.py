from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from .models import Company, QuestionAnswer, JobApplication, Resume, CoverLetter, JobStatus, JobPortalType
from .schemas import CompanyCreate, QuestionAnswerCreate, JobApplicationCreate, ResumeCreate, CoverLetterCreate

class Repository:
    def __init__(self, db: Session):
        self.db = db

    # --- Company Methods ---
    def get_all_companies(self):
        return self.db.query(Company).all()

    def get_company_by_id(self, company_id: int):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_company_by_domain(self, domain: str):
        return self.db.query(Company).filter(Company.domain == domain).first()

    def create_company(self, company: CompanyCreate):
        db_company = Company(**company.model_dump())
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company

    # --- QuestionAnswer Methods ---
    def get_qa_by_company_and_question(self, company_id: int, question_text: str):
        return self.db.query(QuestionAnswer).filter(
            QuestionAnswer.company_id == company_id,
            QuestionAnswer.question_text == question_text
        ).first()

    def create_qa(self, qa: QuestionAnswerCreate):
        db_qa = QuestionAnswer(**qa.model_dump())
        self.db.add(db_qa)
        self.db.commit()
        self.db.refresh(db_qa)
        return db_qa

    # --- JobApplication Methods ---
    def get_all_applications(self):
        return self.db.query(JobApplication).all()

    def get_application_by_id(self, app_id: int):
        return self.db.query(JobApplication).filter(JobApplication.id == app_id).first()

    def create_application(self, app: JobApplicationCreate):
        # Create main application
        db_app = JobApplication(
            company_id=app.company_id,
            domain_extension=app.domain_extension,
            job_status=app.job_status
        )
        self.db.add(db_app)
        self.db.commit()
        self.db.refresh(db_app)
        return db_app

    def update_application_status(self, db_app: JobApplication, status: JobStatus):
        db_app.job_status = status
        self.db.commit()
        self.db.refresh(db_app)
        return db_app

    def get_job_stats(self):
        total = self.db.query(func.count(JobApplication.id)).scalar() or 0
        
        status_results = self.db.query(JobApplication.job_status, func.count(JobApplication.id)).group_by(JobApplication.job_status).all()
        status_counts = {status.value: count for status, count in status_results}
        
        # Join with Company to get portal types
        portal_results = self.db.query(Company.portal_type, func.count(JobApplication.id))\
            .join(JobApplication)\
            .group_by(Company.portal_type).all()
        portal_counts = {portal.value: count for portal, count in portal_results}
        
        daily_results = self.db.query(
            func.date(JobApplication.applied_at).label('date'), 
            func.count(JobApplication.id)
        ).group_by(func.date(JobApplication.applied_at)).order_by(func.date(JobApplication.applied_at).desc()).limit(14).all()
        
        daily_applications = [{"date": str(res[0]), "count": res[1]} for res in daily_results]
        
        return {
            "total_applications": total,
            "status_counts": status_counts,
            "portal_counts": portal_counts,
            "daily_applications": daily_applications
        }

def get_repository(db: Session = Depends(get_db)):
    return Repository(db)
