from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import random
import string

from .models import EmployerProfile, JobPosting, JobApplication, Shortlist
from users.models import User
from apps.workers.models import WorkerProfile


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def job_postings_list(request):
    """
    List all job postings for the authenticated employer (GET)
    Create a new job posting (POST)
    """
    if request.method == 'GET':
        if request.user.user_type == 'admin':
            # Admins can see all job postings
            job_postings = JobPosting.objects.all().order_by('-created_at')
        elif request.user.user_type == 'employer':
            # Employers can see only their own job postings
            job_postings = JobPosting.objects.filter(employer=request.user).order_by('-created_at')
        elif request.user.user_type == 'worker':
            # Workers can see active job postings
            job_postings = JobPosting.objects.filter(is_active=True, status='active').order_by('-created_at')
        else:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Serialize results
        from .serializers import JobPostingListSerializer
        serializer = JobPostingListSerializer(job_postings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.user_type != 'employer':
            return Response(
                {'error': 'Only employers can create job postings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['employer'] = request.user.id
        
        from .serializers import JobPostingCreateSerializer
        serializer = JobPostingCreateSerializer(data=data)
        
        if serializer.is_valid():
            job_posting = serializer.save(employer=request.user)
            from .serializers import JobPostingSerializer
            response_serializer = JobPostingSerializer(job_posting)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def job_posting_detail(request, job_id):
    """
    Retrieve, update or delete a specific job posting
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
    except JobPosting.DoesNotExist:
        return Response(
            {'error': 'Job posting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if (request.user.user_type != 'admin' and 
        request.user.id != job_posting.employer.id):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        from .serializers import JobPostingSerializer
        serializer = JobPostingSerializer(job_posting)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        from .serializers import JobPostingUpdateSerializer
        serializer = JobPostingUpdateSerializer(
            job_posting, 
            data=request.data, 
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            from .serializers import JobPostingSerializer
            response_serializer = JobPostingSerializer(serializer.instance)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        job_posting.delete()
        return Response(
            {'message': 'Job posting deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_applications(request, job_id):
    """
    Get all applications for a specific job posting
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
    except JobPosting.DoesNotExist:
        return Response(
            {'error': 'Job posting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - only employer who posted or admin can see applications
    if (request.user.user_type != 'admin' and 
        request.user.id != job_posting.employer.id):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    applications = JobApplication.objects.filter(job=job_posting).select_related(
        'worker', 'job'
    )
    
    from .serializers import JobApplicationSerializer
    serializer = JobApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_job(request, job_id):
    """
    Apply to a specific job posting
    """
    if request.user.user_type != 'worker':
        return Response(
            {'error': 'Only workers can apply to jobs'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        job_posting = JobPosting.objects.get(id=job_id, is_active=True, status='active')
    except JobPosting.DoesNotExist:
        return Response(
            {'error': 'Job posting not found or not active'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user already applied
    if JobApplication.objects.filter(job=job_posting, worker=request.user).exists():
        return Response(
            {'error': 'You have already applied to this job'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = {
        'job': job_id,
        'worker': request.user.id,
        'cover_letter': request.data.get('cover_letter', ''),
    }
    
    from .serializers import JobApplicationCreateSerializer
    serializer = JobApplicationCreateSerializer(data=data)
    
    if serializer.is_valid():
        application = serializer.save(worker=request.user)
        
        # Send notification to employer
        employer = job_posting.employer
        if employer.email:
            subject = f'New Application for {job_posting.title}'
            message = f'A new worker has applied to your job posting: {job_posting.title}.'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [employer.email],
                fail_silently=True,
            )
        
        from .serializers import JobApplicationSerializer
        response_serializer = JobApplicationSerializer(application)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shortlist_management(request, job_id=None):
    """
    GET: Get shortlisted workers for a job
    POST: Add a worker to shortlist for a job
    """
    if request.user.user_type != 'employer':
        return Response(
            {'error': 'Only employers can manage shortlists'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        # Get all shortlists for the authenticated employer
        shortlists = Shortlist.objects.filter(employer=request.user).select_related(
            'job', 'worker'
        )
        
        from .serializers import ShortlistSerializer
        serializer = ShortlistSerializer(shortlists, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Add a worker to shortlist for a job
        job_id = request.data.get('job_id')
        worker_id = request.data.get('worker_id')
        
        if not job_id or not worker_id:
            return Response(
                {'error': 'Job ID and Worker ID are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = JobPosting.objects.get(id=job_id, employer=request.user)
            worker = User.objects.get(id=worker_id, user_type='worker')
        except (JobPosting.DoesNotExist, User.DoesNotExist):
            return Response(
                {'error': 'Job or Worker not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already shortlisted
        if Shortlist.objects.filter(job=job, worker=worker).exists():
            return Response(
                {'error': 'Worker is already shortlisted for this job'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create shortlist entry
        shortlist_entry = Shortlist.objects.create(
            job=job,
            worker=worker,
            employer=request.user,
            notes=request.data.get('notes', '')
        )
        
        from .serializers import ShortlistSerializer
        serializer = ShortlistSerializer(shortlist_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_shortlist(request, job_id, worker_id):
    """
    Remove a worker from shortlist for a job
    """
    if request.user.user_type != 'employer':
        return Response(
            {'error': 'Only employers can manage shortlists'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        job = JobPosting.objects.get(id=job_id, employer=request.user)
        worker = User.objects.get(id=worker_id, user_type='worker')
        shortlist_entry = Shortlist.objects.get(job=job, worker=worker, employer=request.user)
    except (JobPosting.DoesNotExist, User.DoesNotExist, Shortlist.DoesNotExist):
        return Response(
            {'error': 'Shortlist entry not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    shortlist_entry.delete()
    return Response(
        {'message': 'Worker removed from shortlist successfully'}, 
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employer_profile(request):
    """
    Get the authenticated employer's profile
    """
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        return Response(
            {'error': 'Employer profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    from .serializers import EmployerProfileSerializer
    serializer = EmployerProfileSerializer(employer_profile)
    return Response(serializer.data)