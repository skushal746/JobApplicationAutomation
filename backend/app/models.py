import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from .database import Base

class JobPortalType(str, enum.Enum):
    workday = "workday"
    upwork = "upwork"
    linkedin = "linkedin"
    indeed = "indeed"
    wellfound = "wellfound"
    other = "other"

class JobStatus(str, enum.Enum):
    active = "active"
    applied = "applied"
    screening = "screening"
    technical_interview = "technical_interview"
    final_interview = "final_interview"
    offered = "offered"
    rejected = "rejected"
    not_active = "not_active"

class JobData(Base):
    __tablename__ = "job_datas"

    id = Column(Integer, primary_key=True, index=True)
    job_portal_type = Column(Enum(JobPortalType), default=JobPortalType.other)
    job_url = Column(String(1024))
    job_status = Column(Enum(JobStatus), default=JobStatus.active)
    
    # New tracking fields
    job_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

class FormResponse(Base):
    __tablename__ = "form_responses"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(1024), index=True)
    answer_text = Column(String(1024))
