from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

from .database import engine, Base, get_db
from .models import Job, Proposal, StatusEnum, JobData
from .schemas import Job as JobSchema, Proposal as ProposalSchema, JobData as JobDataSchema, JobDataCreate
from .services.ingestion import mock_ingestion_task

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HITL Job Application Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    # Start the mock ingestion background task
    asyncio.create_task(mock_ingestion_task(manager.broadcast))

@app.get("/jobs", response_model=List[JobSchema])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.get("/jobs/pending", response_model=List[JobSchema])
def get_pending_jobs(db: Session = Depends(get_db)):
    return db.query(Job).join(Proposal).filter(Proposal.status == StatusEnum.PENDING_REVIEW).all()

@app.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: int, content: str, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    proposal.content = content
    proposal.status = StatusEnum.APPROVED
    db.commit()
    return {"status": "approved"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# JobData Management Endpoints
@app.get("/jobdata", response_model=List[JobDataSchema])
def get_job_data(db: Session = Depends(get_db)):
    return db.query(JobData).all()

@app.post("/jobdata", response_model=JobDataSchema)
def create_job_data(job_data: JobDataCreate, db: Session = Depends(get_db)):
    db_job_data = JobData(job_portal_type=job_data.job_portal_type, job_url=job_data.job_url)
    db.add(db_job_data)
    db.commit()
    db.refresh(db_job_data)
    return db_job_data

@app.put("/jobdata/{job_id}", response_model=JobDataSchema)
def update_job_data(job_id: int, job_data: JobDataCreate, db: Session = Depends(get_db)):
    db_job_data = db.query(JobData).filter(JobData.id == job_id).first()
    if not db_job_data:
        raise HTTPException(status_code=404, detail="JobData not found")
    db_job_data.job_portal_type = job_data.job_portal_type
    db_job_data.job_url = job_data.job_url
    db.commit()
    db.refresh(db_job_data)
    return db_job_data
