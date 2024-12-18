from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import JobTitle
from schemas import JobTitle as JobTitleSchema

router = APIRouter()

@router.get("/job_titles", response_model=List[JobTitleSchema])
def get_job_titles(db: Session = Depends(get_db)):
    return db.query(JobTitle).all()

@router.get("/job_titles/{job_id}", response_model=JobTitleSchema)
def get_job_title(job_id: int, db: Session = Depends(get_db)):
    job_title = db.query(JobTitle).filter(JobTitle.job_id == job_id).first()
    if not job_title:
        raise HTTPException(status_code=404, detail="Job title not found")
    return job_title
