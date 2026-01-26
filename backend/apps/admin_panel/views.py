from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from collections import defaultdict

from .models import AdminAction
from apps.workers.models import WorkerProfile
from apps.employers.models import JobPosting, EmployerProfile
from users.models import User
from users.permissions import IsAdminUser
from .serializers import (
    AdminWorkerProfileSerializer,
    AdminJobPostingSerializer,
    AdminUserSerializer,
    AdminAnalyticsSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_worker_profile(request, worker_id):
    """
    Approve a worker profile (admin only)
    """
    try:
        worker_profile = WorkerProfile.objects.select_related('user').get(id=worker_id)
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update approval status
    worker_profile.is_approved = True
    worker_profile.save()

    # Also approve the user account
    worker_profile.user.is_verified = True
    worker_profile.user.save()

    # Log the admin action
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='approve_worker',
        target_user=worker_profile.user,
        target_worker_profile=worker_profile,
        reason=request.data.get('reason', 'Profile approved')
    )

    serializer = AdminWorkerProfileSerializer(worker_profile)
    return Response({
        'message': 'Worker profile approved successfully',
        'worker_profile': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reject_worker_profile(request, worker_id):
    """
    Reject a worker profile (admin only) with reason
    """
    try:
        worker_profile = WorkerProfile.objects.select_related('user').get(id=worker_id)
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update approval status
    worker_profile.is_approved = False
    worker_profile.save()

    # Log the admin action
    reason = request.data.get('reason', 'Profile rejected - no reason provided')
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='reject_worker',
        target_user=worker_profile.user,
        target_worker_profile=worker_profile,
        reason=reason
    )

    serializer = AdminWorkerProfileSerializer(worker_profile)
    return Response({
        'message': 'Worker profile rejected successfully',
        'worker_profile': serializer.data,
        'reason': reason
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def flag_user_account(request, user_id):
    """
    Flag a user account (admin only) with reason
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # In a real system, you might have a flagging system with different severity levels
    # For now, we'll log the action
    reason = request.data.get('reason', 'Account flagged - no reason provided')
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='flag_content',
        target_user=user,
        reason=reason
    )

    serializer = AdminUserSerializer(user)
    return Response({
        'message': 'User account flagged successfully',
        'user': serializer.data,
        'reason': reason
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def suspend_user_account(request, user_id):
    """
    Suspend a user account (admin only) with reason
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Suspend the user account
    user.is_active = False
    user.save()

    # Log the admin action
    reason = request.data.get('reason', 'Account suspended - no reason provided')
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='suspend_user',
        target_user=user,
        reason=reason
    )

    serializer = AdminUserSerializer(user)
    return Response({
        'message': 'User account suspended successfully',
        'user': serializer.data,
        'reason': reason
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_job_posting(request, job_id):
    """
    Approve a job posting (admin only)
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
    except JobPosting.DoesNotExist:
        return Response(
            {'error': 'Job posting not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update job status to active
    if job_posting.status == 'draft':
        job_posting.status = 'active'
    job_posting.is_active = True
    job_posting.save()

    # Log the admin action
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='moderate_job',
        target_job_posting=job_posting,
        reason=request.data.get('reason', 'Job posting approved')
    )

    serializer = AdminJobPostingSerializer(job_posting)
    return Response({
        'message': 'Job posting approved successfully',
        'job_posting': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reject_job_posting(request, job_id):
    """
    Reject a job posting (admin only) with reason
    """
    try:
        job_posting = JobPosting.objects.get(id=job_id)
    except JobPosting.DoesNotExist:
        return Response(
            {'error': 'Job posting not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update job status to closed
    job_posting.status = 'closed'
    job_posting.is_active = False
    job_posting.save()

    # Log the admin action
    reason = request.data.get('reason', 'Job posting rejected - no reason provided')
    AdminAction.objects.create(
        admin_user=request.user,
        action_type='moderate_job',
        target_job_posting=job_posting,
        reason=reason
    )

    serializer = AdminJobPostingSerializer(job_posting)
    return Response({
        'message': 'Job posting rejected successfully',
        'job_posting': serializer.data,
        'reason': reason
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_pending_worker_profiles(request):
    """
    Get all pending worker profiles for review (admin only)
    """
    # Filter for unapproved worker profiles
    pending_profiles = WorkerProfile.objects.filter(is_approved=False).select_related('user').order_by('-created_at')

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)

    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    paginator = Paginator(pending_profiles, per_page)

    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    results = []
    for worker_profile in page_obj:
        serializer = AdminWorkerProfileSerializer(worker_profile)
        data = serializer.data
        data['profile_completeness'] = worker_profile.get_profile_completeness()
        results.append(data)

    response_data = {
        'count': pending_profiles.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': results,
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_pending_job_postings(request):
    """
    Get all pending job postings for review (admin only)
    """
    # Filter for job postings with draft status
    pending_jobs = JobPosting.objects.filter(status='draft').select_related('employer').order_by('-created_at')

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)

    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    paginator = Paginator(pending_jobs, per_page)

    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    results = []
    for job_posting in page_obj:
        serializer = AdminJobPostingSerializer(job_posting)
        results.append(serializer.data)

    response_data = {
        'count': pending_jobs.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': results,
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_accounts(request):
    """
    Get all user accounts with filtering and search capabilities (admin only)
    """
    # Base queryset
    users = User.objects.all().order_by('-date_joined')

    # Apply filters
    user_type = request.query_params.get('user_type', None)
    if user_type:
        users = users.filter(user_type=user_type)

    is_active = request.query_params.get('is_active', None)
    if is_active is not None:
        users = users.filter(is_active=(is_active.lower() == 'true'))

    search = request.query_params.get('search', None)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    # Pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)

    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    paginator = Paginator(users, per_page)

    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    results = []
    for user in page_obj:
        serializer = AdminUserSerializer(user)
        results.append(serializer.data)

    response_data = {
        'count': users.count(),
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': results,
    }

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_worker_statistics(request):
    """
    Get worker statistics by region, skills, education, etc. (admin only)
    """
    # Total worker count
    total_workers = WorkerProfile.objects.count()

    # Count by region
    workers_by_region = WorkerProfile.objects.values('region_of_origin').annotate(
        count=Count('id')
    ).order_by('-count')

    # Count by education level
    workers_by_education = WorkerProfile.objects.values('education_level').annotate(
        count=Count('id')
    ).order_by('-count')

    # Count by religion
    workers_by_religion = WorkerProfile.objects.values('religion').annotate(
        count=Count('id')
    ).order_by('-count')

    # Count by working time preference
    workers_by_worktime = WorkerProfile.objects.values('working_time').annotate(
        count=Count('id')
    ).order_by('-count')

    # Average experience
    avg_experience = WorkerProfile.objects.aggregate(
        avg_exp=Avg('years_experience')
    )['avg_exp'] or 0

    # Average rating
    avg_rating = WorkerProfile.objects.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0.0

    # Count of approved vs unapproved
    approved_count = WorkerProfile.objects.filter(is_approved=True).count()
    unapproved_count = WorkerProfile.objects.filter(is_approved=False).count()

    # Top skills
    all_skills = []
    for profile in WorkerProfile.objects.all():
        all_skills.extend(profile.skills)

    skill_counts = defaultdict(int)
    for skill in all_skills:
        skill_counts[skill] += 1

    # Get top 10 skills
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return Response({
        'total_workers': total_workers,
        'workers_by_region': list(workers_by_region),
        'workers_by_education': list(workers_by_education),
        'workers_by_religion': list(workers_by_religion),
        'workers_by_worktime': list(workers_by_worktime),
        'average_experience': avg_experience,
        'average_rating': float(avg_rating),
        'approved_count': approved_count,
        'unapproved_count': unapproved_count,
        'top_skills': top_skills
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_registration_trends(request):
    """
    Get registration trends for workers and employers (admin only)
    """
    # Get date range parameters
    days = int(request.query_params.get('days', 30))  # Default to 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Registration trends for workers
    worker_registrations = []
    employer_registrations = []

    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    for date in date_range:
        # Format date for display
        date_str = date.strftime('%Y-%m-%d')

        # Count worker registrations for this date
        worker_count = User.objects.filter(
            user_type='worker',
            date_joined__date=date
        ).count()

        # Count employer registrations for this date
        employer_count = User.objects.filter(
            user_type='employer',
            date_joined__date=date
        ).count()

        worker_registrations.append({
            'date': date_str,
            'count': worker_count
        })

        employer_registrations.append({
            'date': date_str,
            'count': employer_count
        })

    # Get total counts
    total_workers = User.objects.filter(user_type='worker').count()
    total_employers = User.objects.filter(user_type='employer').count()

    return Response({
        'date_range': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        },
        'worker_registrations': worker_registrations,
        'employer_registrations': employer_registrations,
        'total_workers': total_workers,
        'total_employers': total_employers,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def export_worker_data(request):
    """
    Export worker data to CSV format (admin only)
    """
    # Get all worker profiles with related user data
    worker_profiles = WorkerProfile.objects.select_related('user').all()

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="worker_data_export.csv"'

    writer = csv.writer(response)

    # Write the header
    writer.writerow([
        'ID', 'Username', 'Full Name', 'Age', 'Place of Birth', 'Region of Origin',
        'Current Location', 'Languages', 'Education Level', 'Religion', 'Working Time',
        'Skills', 'Years Experience', 'Background Check Status', 'Is Approved', 'Rating',
        'Created At', 'User Verified'
    ])

    # Write the data rows
    for profile in worker_profiles:
        writer.writerow([
            profile.id,
            profile.user.username,
            profile.full_name,
            profile.age,
            profile.place_of_birth,
            profile.region_of_origin,
            profile.current_location,
            '; '.join([lang if isinstance(lang, str) else str(lang) for lang in profile.languages]),
            profile.get_education_level_display(),
            profile.get_religion_display(),
            profile.get_working_time_display(),
            '; '.join(profile.skills),
            profile.years_experience,
            profile.background_check_status,
            profile.is_approved,
            float(profile.rating),
            profile.created_at,
            profile.user.is_verified
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def export_job_data(request):
    """
    Export job posting data to CSV format (admin only)
    """
    # Get all job postings with related employer data
    job_postings = JobPosting.objects.select_related('employer').all()

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_data_export.csv"'

    writer = csv.writer(response)

    # Write the header
    writer.writerow([
        'ID', 'Title', 'Description', 'Location', 'City', 'Region', 'Salary Min',
        'Salary Max', 'Required Skills', 'Working Arrangement', 'Experience Required',
        'Education Required', 'Religion Preference', 'Age Min', 'Age Max',
        'Language Requirements', 'Start Date', 'End Date', 'Is Active', 'Status',
        'Posted by', 'Created At'
    ])

    # Write the data rows
    for job in job_postings:
        writer.writerow([
            job.id,
            job.title,
            job.description,
            job.location,
            job.city,
            job.region,
            job.salary_min,
            job.salary_max,
            '; '.join(job.required_skills),
            job.get_working_arrangement_display(),
            job.experience_required,
            job.education_required,
            job.religion_preference,
            job.age_preference_min or '',
            job.age_preference_max or '',
            '; '.join(job.language_requirements),
            job.start_date,
            job.end_date or '',
            job.is_active,
            job.get_status_display(),
            job.employer.username,
            job.created_at
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_platform_analytics(request):
    """
    Get comprehensive platform analytics (admin only)
    """
    # User statistics
    total_users = User.objects.count()
    total_workers = User.objects.filter(user_type='worker').count()
    total_employers = User.objects.filter(user_type='employer').count()
    total_admins = User.objects.filter(user_type='admin').count()

    # Profile statistics
    total_worker_profiles = WorkerProfile.objects.count()
    approved_worker_profiles = WorkerProfile.objects.filter(is_approved=True).count()
    unapproved_worker_profiles = WorkerProfile.objects.filter(is_approved=False).count()

    # Job statistics
    total_job_postings = JobPosting.objects.count()
    active_job_postings = JobPosting.objects.filter(is_active=True, status='active').count()
    inactive_job_postings = JobPosting.objects.filter(is_active=False).count()

    # Registration trends for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago)

    # Registration by user type in the last 30 days
    recent_workers = recent_registrations.filter(user_type='worker').count()
    recent_employers = recent_registrations.filter(user_type='employer').count()

    # Average profile completeness
    avg_profile_completeness = 0
    if total_worker_profiles > 0:
        completeness_sum = sum([wp.get_profile_completeness() for wp in WorkerProfile.objects.all()])
        avg_profile_completeness = completeness_sum / total_worker_profiles

    # Calculate approval rate
    approval_rate = 0
    if total_worker_profiles > 0:
        approval_rate = (approved_worker_profiles / total_worker_profiles) * 100

    return Response({
        'user_statistics': {
            'total_users': total_users,
            'total_workers': total_workers,
            'total_employers': total_employers,
            'total_admins': total_admins,
        },
        'profile_statistics': {
            'total_worker_profiles': total_worker_profiles,
            'approved_worker_profiles': approved_worker_profiles,
            'unapproved_worker_profiles': unapproved_worker_profiles,
            'approval_rate': round(approval_rate, 2),
            'average_profile_completeness': round(avg_profile_completeness, 2),
        },
        'job_statistics': {
            'total_job_postings': total_job_postings,
            'active_job_postings': active_job_postings,
            'inactive_job_postings': inactive_job_postings,
        },
        'registration_trends': {
            'recent_workers': recent_workers,
            'recent_employers': recent_employers,
            'days_count': 30,
        }
    })
