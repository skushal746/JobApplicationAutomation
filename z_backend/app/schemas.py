from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from .models import JobPortalType, JobStatus

# --- Company Schemas ---
class CompanyBase(BaseModel):
    name: str
    username: Optional[str] = None
    password: Optional[str] = None
    domain: Optional[str] = None
    portal_type: JobPortalType = JobPortalType.workday
    is_default: bool = False

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- QuestionAnswer Schemas ---
class QuestionAnswerBase(BaseModel):
    question_text: str
    answer_text: str
    company_id: int

class QuestionAnswerCreate(QuestionAnswerBase):
    pass

class QuestionAnswer(QuestionAnswerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Resume & CoverLetter Schemas ---
class ResumeBase(BaseModel):
    location: str
    job_application_id: int

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CoverLetterBase(BaseModel):
    location: str
    job_application_id: int

class CoverLetterCreate(CoverLetterBase):
    pass

class CoverLetter(CoverLetterBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- JobApplication Schemas ---
class JobApplicationBase(BaseModel):
    company_id: int
    domain_extension: str = "en-US"
    job_status: JobStatus = JobStatus.active

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplication(JobApplicationBase):
    id: int
    applied_at: datetime
    resumes: List[Resume] = []
    cover_letters: List[CoverLetter] = []
    model_config = ConfigDict(from_attributes=True)

# --- Stats ---
class JobStats(BaseModel):
    total_applications: int
    status_counts: Dict[str, int]
    portal_counts: Dict[str, int]
    daily_applications: List[Dict[str, any]]
