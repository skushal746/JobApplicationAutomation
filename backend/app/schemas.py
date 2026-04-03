from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from .models import JobPortalType, JobStatus

class JobDataBase(BaseModel):
    job_portal_type: JobPortalType
    job_url: str
    job_status: JobStatus = JobStatus.active
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None

class JobDataCreate(JobDataBase):
    pass

class JobData(JobDataBase):
    id: int
    applied_at: datetime

    class Config:
        from_attributes = True

class JobStats(BaseModel):
    total_applications: int
    status_counts: Dict[str, int]
    portal_counts: Dict[str, int]
    daily_applications: List[Dict[str, any]] # e.g. [{"date": "2024-03-20", "count": 5}]

class FormResponseBase(BaseModel):
    question_text: str
    answer_text: str

class FormResponseCreate(FormResponseBase):
    pass

class FormResponse(FormResponseBase):
    id: int

    class Config:
        from_attributes = True
