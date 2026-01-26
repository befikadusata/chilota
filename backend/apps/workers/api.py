"""
Workers API endpoints using Django Ninja
"""
from ninja import Router
from typing import List, Optional
from workers.schemas import (
    WorkerProfileCreateSchema,
    WorkerProfileUpdateSchema,
    WorkerProfileOutSchema,
    WorkerSearchSchema,
    SearchFiltersSchema
)
from workers.models import WorkerProfile
from users.auth import JWTAuth
from django.core.paginator import Paginator
from django.db.models import Q

router = Router()


@router.get("/", response=List[WorkerProfileOutSchema], auth=JWTAuth())
def list_workers(request):
    """
    List all worker profiles
    """
    workers = WorkerProfile.objects.all()
    return workers


@router.post("/", response=WorkerProfileOutSchema, auth=JWTAuth())
def create_worker_profile(request, data: WorkerProfileCreateSchema):
    """
    Create a new worker profile
    """
    # Create the worker profile
    worker_profile = WorkerProfile.objects.create(
        user=request.auth,
        **data.dict()
    )
    return worker_profile


@router.get("/{worker_id}/", response=WorkerProfileOutSchema)
def get_worker_profile(request, worker_id: int):
    """
    Get a specific worker profile
    """
    try:
        worker_profile = WorkerProfile.objects.get(id=worker_id)
        return worker_profile
    except WorkerProfile.DoesNotExist:
        return {"detail": "Worker profile not found"}, 404


@router.put("/{worker_id}/", response=WorkerProfileOutSchema, auth=JWTAuth())
def update_worker_profile(request, worker_id: int, data: WorkerProfileUpdateSchema):
    """
    Update a worker profile
    """
    try:
        worker_profile = WorkerProfile.objects.get(id=worker_id, user=request.auth)
        
        # Update fields
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(worker_profile, attr, value)
        worker_profile.save()
        
        return worker_profile
    except WorkerProfile.DoesNotExist:
        return {"detail": "Worker profile not found"}, 404


@router.delete("/{worker_id}/", auth=JWTAuth())
def delete_worker_profile(request, worker_id: int):
    """
    Delete a worker profile
    """
    try:
        worker_profile = WorkerProfile.objects.get(id=worker_id, user=request.auth)
        worker_profile.delete()
        return {"success": True}
    except WorkerProfile.DoesNotExist:
        return {"detail": "Worker profile not found"}, 404


@router.post("/search/", response=List[WorkerProfileOutSchema])
def advanced_worker_search(request, filters: WorkerSearchSchema):
    """
    Advanced search for workers based on multiple criteria
    """
    queryset = WorkerProfile.objects.all()
    
    # Apply filters
    if filters.region:
        queryset = queryset.filter(region__icontains=filters.region)
    if filters.skills:
        for skill in filters.skills:
            queryset = queryset.filter(skills__icontains=skill)
    if filters.min_experience:
        queryset = queryset.filter(years_of_experience__gte=filters.min_experience)
    if filters.max_experience:
        queryset = queryset.filter(years_of_experience__lte=filters.max_experience)
    if filters.age_min:
        queryset = queryset.filter(age__gte=filters.age_min)
    if filters.age_max:
        queryset = queryset.filter(age__lte=filters.age_max)
    if filters.gender:
        queryset = queryset.filter(gender=filters.gender)
    if filters.language:
        queryset = queryset.filter(languages__icontains=filters.language)
    
    # Apply pagination
    paginator = Paginator(queryset, filters.page_size or 20)
    page = paginator.get_page(filters.page or 1)
    
    return list(page)


@router.get("/filters/", response=SearchFiltersSchema)
def get_search_filters(request):
    """
    Get available filter options for worker search
    """
    # This would return dynamic values based on the data in the system
    from jobs.models import Region, Skill, Language
    
    regions = list(Region.objects.values_list('name', flat=True))
    skills = list(Skill.objects.values_list('name', flat=True))
    languages = list(Language.objects.values_list('name', flat=True))
    
    return SearchFiltersSchema(
        regions=regions,
        skills=skills,
        languages=languages,
        genders=["Male", "Female", "Other"]
    )