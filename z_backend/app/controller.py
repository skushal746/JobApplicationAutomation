from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from .schemas import CompanyCreate, Company as CompanySchema
from .schemas import QuestionAnswerCreate, QuestionAnswer as QASchema
from .schemas import JobApplicationCreate, JobApplication as AppSchema, JobStats
from .service import Service, get_service

router = APIRouter()

# --- Company Endpoints ---
@router.post("/companies", response_model=CompanySchema)
def create_company(company: CompanyCreate, service: Service = Depends(get_service)):
    return service.create_company(company)

@router.get("/companies", response_model=List[CompanySchema])
def get_companies(service: Service = Depends(get_service)):
    return service.get_companies()

@router.get("/companies/{company_id}", response_model=CompanySchema)
def get_company(company_id: int, service: Service = Depends(get_service)):
    result = service.get_company(company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Company not found")
    return result

# --- QuestionAnswer Endpoints ---
@router.post("/qa", response_model=QASchema)
def create_qa(qa: QuestionAnswerCreate, service: Service = Depends(get_service)):
    return service.create_qa(qa)

# --- JobApplication Endpoints ---
@router.post("/applications", response_model=AppSchema)
async def create_application(
    app: JobApplicationCreate, 
    background_tasks: BackgroundTasks,
    service: Service = Depends(get_service)
):
    db_app = service.create_application(app)
    # Trigger automation instantly in the background
    background_tasks.add_task(service.trigger_automation, db_app.id)
    return db_app

@router.get("/applications", response_model=List[AppSchema])
def get_applications(service: Service = Depends(get_service)):
    return service.get_applications()

@router.get("/applications/{app_id}", response_model=AppSchema)
def get_application(app_id: int, service: Service = Depends(get_service)):
    result = service.get_application(app_id)
    if not result:
        raise HTTPException(status_code=404, detail="Application not found")
    return result

@router.get("/stats", response_model=JobStats)
def get_job_stats(service: Service = Depends(get_service)):
    return service.get_job_stats()

@router.post("/automate/all")
async def automate_all(service: Service = Depends(get_service)):
    count = await service.automate_all_pending()
    return {"status": "success", "count": count}
