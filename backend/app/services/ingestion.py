import asyncio
import random
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Job, Proposal, StatusEnum
from .ai_service import generate_proposal
import json

MOCK_JOBS = [
    {
        "title": "FastAPI Backend Developer",
        "description": "Looking for an expert in FastAPI and WebSockets to build a real-time dashboard.",
        "budget": "$50/hr",
        "skills": "Python, FastAPI, WebSockets"
    },
    {
        "title": "React Frontend Engineer",
        "description": "Need a React developer proficient in TypeScript and Tailwind CSS for a dashboard project.",
        "budget": "$40/hr",
        "skills": "React, TypeScript, Tailwind"
    },
    {
        "title": "Full Stack Architect",
        "description": "Seeking a developer to build a HITL pipeline for job applications.",
        "budget": "$60/hr",
        "skills": "Python, React, AI"
    }
]

async def mock_ingestion_task(broadcast_func):
    while True:
        # Simulate polling every 30 seconds
        await asyncio.sleep(30)
        
        job_data = random.choice(MOCK_JOBS)
        db = SessionLocal()
        try:
            # Check if job already exists (simple title check for mock)
            existing = db.query(Job).filter(Job.title == job_data["title"]).first()
            if existing:
                continue

            # Create Job
            new_job = Job(**job_data, source="mock_rss")
            db.add(new_job)
            db.commit()
            db.refresh(new_job)

            # Generate Proposal
            proposal_content = generate_proposal(
                new_job.title, 
                new_job.description, 
                new_job.skills or ""
            )
            
            # Create Proposal
            new_proposal = Proposal(
                job_id=new_job.id,
                content=proposal_content,
                status=StatusEnum.PENDING_REVIEW
            )
            db.add(new_proposal)
            db.commit()
            
            # Emit WebSocket event
            await broadcast_func({
                "type": "new_job",
                "data": {
                    "id": new_job.id,
                    "title": new_job.title,
                    "description": new_job.description,
                    "proposal": proposal_content
                }
            })
            print(f"Ingested and drafted proposal for: {new_job.title}")

        except Exception as e:
            print(f"Ingestion error: {e}")
        finally:
            db.close()
