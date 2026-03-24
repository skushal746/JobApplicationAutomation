from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .models import StatusEnum, JobPortalType

class ProposalBase(BaseModel):
    content: str
    status: StatusEnum

class ProposalCreate(ProposalBase):
    job_id: int

class Proposal(ProposalBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    title: str
    description: str
    budget: Optional[str] = None
    skills: Optional[str] = None
    source: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    created_at: datetime
    proposal: Optional[Proposal] = None

    class Config:
        from_attributes = True

class JobDataBase(BaseModel):
    job_portal_type: JobPortalType
    job_url: str

class JobDataCreate(JobDataBase):
    pass

class JobData(JobDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
