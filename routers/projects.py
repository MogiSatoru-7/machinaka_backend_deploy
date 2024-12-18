from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Project
from schemas import Project as ProjectSchema, ProjectBase

router = APIRouter()

@router.get("/projects", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects", response_model=ProjectSchema)
def create_project(project: ProjectBase, db: Session = Depends(get_db)):
    new_project = Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# @router.get("/projects", response_model=List[schemas.Project])
# async def get_projects(db: Session = Depends(get_db)):
#     projects = db.query(models.Project).all()
#     print(projects)  # デバッグ用
#     return projects
