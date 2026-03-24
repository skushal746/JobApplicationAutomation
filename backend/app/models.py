from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class JobPortalType(str, enum.Enum):
    WORKDAY = "workday"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    proposal = relationship("Proposal", back_populates="job", uselist=False)

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    content = Column(Text, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING_REVIEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="proposal")

class JobData(Base):
    __tablename__ = "job_datas"

    id = Column(Integer, primary_key=True, index=True)
    job_portal_type = Column(Enum(JobPortalType), nullable=False, default=JobPortalType.WORKDAY)
    job_url = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
