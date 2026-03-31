from pydantic import BaseModel
from .models import JobPortalType, JobStatus

class JobDataBase(BaseModel):
    job_portal_type: JobPortalType
    job_url: str
    job_status: JobStatus = JobStatus.active

class JobDataCreate(JobDataBase):
    pass

class JobData(JobDataBase):
    id: int

    class Config:
        from_attributes = True

class FormResponseBase(BaseModel):
    question_text: str
    answer_text: str

class FormResponseCreate(FormResponseBase):
    pass

class FormResponse(FormResponseBase):
    id: int

    class Config:
        from_attributes = True
