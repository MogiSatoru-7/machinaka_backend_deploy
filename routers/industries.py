from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Industry
from schemas import Industry as IndustrySchema

router = APIRouter()

@router.get("/industries", response_model=List[IndustrySchema])
def get_industries(db: Session = Depends(get_db)):
    return db.query(Industry).all()

@router.get("/industries/{industry_id}", response_model=IndustrySchema)
def get_industry(industry_id: int, db: Session = Depends(get_db)):
    industry = db.query(Industry).filter(Industry.industry_id == industry_id).first()
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return industry
