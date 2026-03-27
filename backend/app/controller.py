from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .schemas import JobData as JobDataSchema, JobDataCreate
from .service import Service, get_service

router = APIRouter()

@router.get("/jobdata", response_model=List[JobDataSchema])
def get_job_data(service: Service = Depends(get_service)):
    return service.get_job_data()

@router.post("/jobdata", response_model=JobDataSchema)
def create_job_data(job_data: JobDataCreate, service: Service = Depends(get_service)):
    return service.create_job_data(job_data)

@router.put("/jobdata/{job_id}", response_model=JobDataSchema)
def update_job_data(job_id: int, job_data: JobDataCreate, service: Service = Depends(get_service)):
    result = service.update_job_data(job_id, job_data)
    if not result:
        raise HTTPException(status_code=404, detail="JobData not found")
    return result

@router.get("/jobdata/{job_id}", response_model=JobDataSchema)
def get_job_data_by_id(job_id: int, service: Service = Depends(get_service)):
    result = service.get_job_data_by_id(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="JobData not found")
    return result

@router.delete("/jobdata/{job_id}")
def delete_job_data(job_id: int, service: Service = Depends(get_service)):
    result = service.delete_job_data(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="JobData not found")
    return {"status": "deleted"}
