# schemas.py

from pydantic import BaseModel
from typing import List, Optional


class OfficeBase(BaseModel):
    office_name: str
    address: str
    area: str
    access: Optional[str]
    capacity: Optional[int]
    tags: Optional[str]
    latitude: Optional[float]  # 修正: str -> float
    longitude: Optional[float]  # 修正: str -> float


class Office(OfficeBase):
    office_id: int
    class Config:
        from_attributes = True  # orm_mode を置き換え


class ProjectBase(BaseModel):
    project_name: str
    project_description: Optional[str]
    project_image_url: Optional[str]  # 追加: 画像URL


class Project(ProjectBase):
    project_id: int
    user_id: int
    project_image_url: Optional[str]  # この行が必要
    class Config:
        from_attributes = True  # orm_mode を置き換え


class SkillBase(BaseModel):
    skill_name: str
    skill_description: Optional[str]


class Skill(SkillBase):
    skill_id: int
    user_id: int
    class Config:
        from_attributes = True  # orm_mode を置き換え


class JobTitleBase(BaseModel):
    job_title: str


class JobTitle(JobTitleBase):
    job_id: int
    class Config:
        from_attributes = True  # orm_mode を置き換え


class IndustryBase(BaseModel):
    industry_name: str


class Industry(IndustryBase):
    industry_id: int
    class Config:
        from_attributes = True  # orm_mode を置き換え


class UserBase(BaseModel):
    user_name: str
    user_type: str


class User(UserBase):
    user_id: int
    office_id: int
    job_id: int
    industry_id: int
    projects: List[Project] = []
    skills: List[Skill] = []
    class Config:
        from_attributes = True  # orm_mode を置き換え
