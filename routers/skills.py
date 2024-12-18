from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Skill
from schemas import Skill as SkillSchema, SkillBase

router = APIRouter()

@router.get("/skills", response_model=List[SkillSchema])
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()

@router.get("/skills/{skill_id}", response_model=SkillSchema)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.post("/skills", response_model=SkillSchema)
def create_skill(skill: SkillBase, db: Session = Depends(get_db)):
    new_skill = Skill(**skill.dict())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill
