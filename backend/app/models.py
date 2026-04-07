import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class JobPortalType(str, enum.Enum):
    workday = "workday"
    linkedin = "linkedin"

class JobStatus(str, enum.Enum):
    active = "active"
    applied = "applied"
    not_active = "not_active"

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    portal_type = Column(Enum(JobPortalType), default=JobPortalType.workday)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    question_answers = relationship("QuestionAnswer", back_populates="company", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="company", cascade="all, delete-orphan")

class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    question_text = Column(String(1024), nullable=False)
    answer_text = Column(String(1024), nullable=False)
    
    company = relationship("Company", back_populates="question_answers")

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    domain_extension = Column(String(100), default="en-US")
    job_status = Column(Enum(JobStatus), default=JobStatus.active)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="job_applications")
    resumes = relationship("Resume", back_populates="job_application", cascade="all, delete-orphan")
    cover_letters = relationship("CoverLetter", back_populates="job_application", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"))
    location = Column(String(1024), nullable=False) # Local file path
    
    job_application = relationship("JobApplication", back_populates="resumes")

class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"))
    location = Column(String(1024), nullable=False) # Local file path
    
    job_application = relationship("JobApplication", back_populates="cover_letters")
