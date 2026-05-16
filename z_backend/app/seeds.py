from sqlalchemy.orm import Session
from .models import Company, QuestionAnswer, JobPortalType, JobStatus, JobApplication
import logging

logger = logging.getLogger(__name__)

def seed_data(db: Session):
    """
    Seeds the database with initial dummy data if it's empty.
    """
    # Check if any company exists
    if db.query(Company).first():
        logger.info("Database already contains data, skipping seed.")
        return

    logger.info("Seeding database with dummy data...")

    # 1. Create Dummy Companies
    companies = [
        Company(
            name="Google",
            domain="google.com",
            portal_type=JobPortalType.workday,
            is_default=True,
            username="john_doe_google",
            password="secret_password"
        ),
        Company(
            name="Microsoft",
            domain="microsoft.com",
            portal_type=JobPortalType.workday,
            is_default=False,
            username="john_doe_msft",
            password="secret_password"
        ),
        Company(
            name="Meta",
            domain="meta.com",
            portal_type=JobPortalType.workday,
            is_default=False,
            username="john_doe_meta",
            password="secret_password"
        ),
        Company(
            name="Generic Startup",
            domain="linkedin.com",
            portal_type=JobPortalType.linkedin,
            is_default=False
        )
    ]
    
    db.add_all(companies)
    db.commit()
    
    # Refresh to get IDs
    for company in companies:
        db.refresh(company)

    # 2. Add Dummy Question-Answers for the default company (Google)
    google = next(c for c in companies if c.name == "Google")
    qa_pairs = [
        QuestionAnswer(
            company_id=google.id,
            question_text="What is your full name?",
            answer_text="John Alex Doe"
        ),
        QuestionAnswer(
            company_id=google.id,
            question_text="How many years of experience do you have with Python?",
            answer_text="5 years"
        ),
        QuestionAnswer(
            company_id=google.id,
            question_text="Are you authorized to work in the United States?",
            answer_text="Yes"
        )
    ]
    db.add_all(qa_pairs)

    # 3. Add a Dummy Job Application
    dummy_app = JobApplication(
        company_id=google.id,
        domain_extension="en-US",
        job_status=JobStatus.active
    )
    db.add(dummy_app)

    db.commit()
    logger.info("Database seeding completed.")
