"""
Schemas for the workers API
"""
from ninja import Schema
from typing import List, Optional
from datetime import date


class WorkerProfileCreateSchema(Schema):
    fayda_id: str
    full_name: str
    age: int
    place_of_birth: str
    region_of_origin: str
    current_location: str
    emergency_contact_name: str
    emergency_contact_phone: str
    languages: List[dict]
    education_level: str
    religion: str
    working_time: str
    skills: List[str]
    years_experience: int


class WorkerProfileUpdateSchema(Schema):
    fayda_id: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    place_of_birth: Optional[str] = None
    region_of_origin: Optional[str] = None
    current_location: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    languages: Optional[List[dict]] = None
    education_level: Optional[str] = None
    religion: Optional[str] = None
    working_time: Optional[str] = None
    skills: Optional[List[str]] = None
    years_experience: Optional[int] = None
    profile_photo: Optional[str] = None
    background_check_status: Optional[bool] = None
    is_approved: Optional[bool] = None
    rating: Optional[float] = None


class WorkerProfileOutSchema(Schema):
    id: int
    user_id: int
    fayda_id: str
    full_name: str
    age: int
    place_of_birth: str
    region_of_origin: str
    current_location: str
    emergency_contact_name: str
    emergency_contact_phone: str
    languages: List[dict]
    education_level: str
    religion: str
    working_time: str
    skills: List[str]
    years_experience: int
    profile_photo: Optional[str] = None
    background_check_status: bool
    is_approved: bool
    rating: float
    created_at: date
    updated_at: date


class WorkerSearchSchema(Schema):
    region: Optional[str] = None
    skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20


class SearchFiltersSchema(Schema):
    regions: List[str]
    skills: List[str]
    languages: List[str]
    genders: List[str]