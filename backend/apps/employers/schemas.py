"""
Schemas for the employers API
"""
from ninja import Schema
from typing import List, Optional
from datetime import date


class JobPostingCreateSchema(Schema):
    title: str
    description: str
    region: str
    city: str
    woreda: str
    kebele: str
    job_category: str
    required_skills: List[str]
    min_experience: int
    education_requirement: str
    language_requirements: List[str]
    working_time: str
    wage: float
    wage_unit: str
    benefits: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True


class JobPostingUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    woreda: Optional[str] = None
    kebele: Optional[str] = None
    job_category: Optional[str] = None
    required_skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    education_requirement: Optional[str] = None
    language_requirements: Optional[List[str]] = None
    working_time: Optional[str] = None
    wage: Optional[float] = None
    wage_unit: Optional[str] = None
    benefits: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class JobPostingOutSchema(Schema):
    id: int
    employer_id: int
    title: str
    description: str
    region: str
    city: str
    woreda: str
    kebele: str
    job_category: str
    required_skills: List[str]
    min_experience: int
    education_requirement: str
    language_requirements: List[str]
    working_time: str
    wage: float
    wage_unit: str
    benefits: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool
    created_at: date
    updated_at: date


class JobApplicationCreateSchema(Schema):
    cover_letter: str
    resume: Optional[str] = None


class JobApplicationOutSchema(Schema):
    id: int
    job_posting_id: int
    applicant_id: int
    cover_letter: str
    resume: Optional[str] = None
    status: str
    applied_at: date