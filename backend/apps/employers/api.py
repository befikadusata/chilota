"""
Employers API endpoints using Django Ninja
"""
from ninja import Router
from typing import List
from employers.schemas import (
    JobPostingCreateSchema,
    JobPostingUpdateSchema,
    JobPostingOutSchema,
    JobApplicationCreateSchema,
    JobApplicationOutSchema
)
from employers.models import JobPosting, JobApplication
from users.auth import JWTAuth

router = Router()


@router.get("/jobs/", response=List[JobPostingOutSchema], auth=JWTAuth())
def list_job_postings(request):
    """
    List all job postings
    """
    jobs = JobPosting.objects.all()
    return jobs


@router.post("/jobs/", response=JobPostingOutSchema, auth=JWTAuth())
def create_job_posting(request, data: JobPostingCreateSchema):
    """
    Create a new job posting
    """
    job_posting = JobPosting.objects.create(
        employer=request.auth.employerprofile,  # Assuming user has an employer profile
        **data.dict()
    )
    return job_posting


@router.get("/jobs/{job_id}/", response=JobPostingOutSchema)
def get_job_posting(request, job_id: int):
    """
    Get a specific job posting
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
        return job_posting
    except JobPosting.DoesNotExist:
        return {"detail": "Job posting not found"}, 404


@router.put("/jobs/{job_id}/", response=JobPostingOutSchema, auth=JWTAuth())
def update_job_posting(request, job_id: int, data: JobPostingUpdateSchema):
    """
    Update a job posting
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id, employer=request.auth.employerprofile)
        
        # Update fields
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(job_posting, attr, value)
        job_posting.save()
        
        return job_posting
    except JobPosting.DoesNotExist:
        return {"detail": "Job posting not found"}, 404


@router.delete("/jobs/{job_id}/", auth=JWTAuth())
def delete_job_posting(request, job_id: int):
    """
    Delete a job posting
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id, employer=request.auth.employerprofile)
        job_posting.delete()
        return {"success": True}
    except JobPosting.DoesNotExist:
        return {"detail": "Job posting not found"}, 404


@router.post("/jobs/{job_id}/apply/", response=JobApplicationOutSchema, auth=JWTAuth())
def apply_for_job(request, job_id: int, data: JobApplicationCreateSchema):
    """
    Apply for a job
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
        
        # Create job application
        application = JobApplication.objects.create(
            job_posting=job_posting,
            applicant=request.auth.workerprofile,  # Assuming user has a worker profile
            cover_letter=data.cover_letter,
            resume=data.resume
        )
        
        return application
    except JobPosting.DoesNotExist:
        return {"detail": "Job posting not found"}, 404


@router.get("/applications/", response=List[JobApplicationOutSchema], auth=JWTAuth())
def list_applications(request):
    """
    List job applications for the authenticated user
    """
    applications = JobApplication.objects.filter(applicant=request.auth.workerprofile)
    return applications