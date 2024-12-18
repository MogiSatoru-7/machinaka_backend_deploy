from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Office
from schemas import Office as OfficeSchema

router = APIRouter()

@router.get("/offices", response_model=List[OfficeSchema])
def get_offices(db: Session = Depends(get_db)):
    return db.query(Office).all()

@router.get("/offices/{office_id}", response_model=OfficeSchema)
def get_office(office_id: int, db: Session = Depends(get_db)):
    office = db.query(Office).filter(Office.office_id == office_id).first()
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    return office
