import enum
from sqlalchemy import Column, Integer, String, Enum
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
    not_active = "not_active"

class JobData(Base):
    __tablename__ = "job_datas"

    id = Column(Integer, primary_key=True, index=True)
    job_portal_type = Column(Enum(JobPortalType), default=JobPortalType.other)
    job_url = Column(String(1024))
    job_status = Column(Enum(JobStatus), default=JobStatus.active)
