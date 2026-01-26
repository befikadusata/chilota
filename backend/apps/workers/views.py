from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Avg, Min, Max
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import hashlib
from django.core.cache import cache

from .models import WorkerProfile
from users.models import User
from apps.jobs.models import Skill, Language, Region, EducationLevel, Religion


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advanced_worker_search(request):
    """
    Advanced worker search API with filtering by multiple criteria
    """
    # Create cache key based on all query parameters
    query_params = dict(request.query_params)
    cache_key = f"worker_search_{hashlib.md5(str(sorted(query_params.items())).encode()).hexdigest()}"
    
    # Check if results are already cached
    cached_results = cache.get(cache_key)
    if cached_results:
        return Response(cached_results, status=status.HTTP_200_OK)
    
    # Initialize filters with non-JSON fields only (for SQLite compatibility)
    filters = Q()
    
    # Filter by region of origin
    region_origin = request.query_params.get('region_of_origin', None)
    if region_origin:
        filters &= Q(region_of_origin__icontains=region_origin)
    
    # Filter by current location
    current_location = request.query_params.get('current_location', None)
    if current_location:
        filters &= Q(current_location__icontains=current_location)
    
    # Filter by years of experience (min and max)
    experience_min = request.query_params.get('experience_min', None)
    if experience_min:
        try:
            filters &= Q(years_experience__gte=int(experience_min))
        except ValueError:
            pass
    
    experience_max = request.query_params.get('experience_max', None)
    if experience_max:
        try:
            filters &= Q(years_experience__lte=int(experience_max))
        except ValueError:
            pass
    
    # Filter by education level
    education_levels = request.query_params.getlist('education_level')
    if education_levels:
        filters &= Q(education_level__in=education_levels)
    
    # Filter by religion
    religions = request.query_params.getlist('religion')
    if religions:
        filters &= Q(religion__in=religions)
    
    # Filter by age range
    age_min = request.query_params.get('age_min', None)
    if age_min:
        try:
            filters &= Q(age__gte=int(age_min))
        except ValueError:
            pass
    
    age_max = request.query_params.get('age_max', None)
    if age_max:
        try:
            filters &= Q(age__lte=int(age_max))
        except ValueError:
            pass
    
    # Filter by working time preference
    working_time = request.query_params.get('working_time', None)
    if working_time:
        filters &= Q(working_time=working_time)
    
    # Filter by verification status
    is_verified = request.query_params.get('is_verified', None)
    if is_verified and is_verified.lower() == 'true':
        filters &= Q(user__is_verified=True)
    
    # Filter by approval status
    is_approved = request.query_params.get('is_approved', None)
    if is_approved and is_approved.lower() == 'true':
        filters &= Q(is_approved=True)
    
    # Filter by rating
    min_rating = request.query_params.get('min_rating', None)
    if min_rating:
        try:
            filters &= Q(rating__gte=float(min_rating))
        except ValueError:
            pass
    
    # Filter by skills
    skills = request.query_params.getlist('skills')
    if skills:
        filters &= Q(skills__contains=skills)

    # Filter by languages
    languages = request.query_params.getlist('languages')
    if languages:
        filters &= Q(languages__contains=languages)
    
    # Apply base filters (those that work with database queries)
    queryset = WorkerProfile.objects.select_related('user').filter(filters)

    # Apply sorting
    sort_by = request.query_params.get('sort_by', 'relevance')  # Default to relevance

    if sort_by == 'relevance':
        # Default ordering by user creation date, but could be enhanced
        queryset = queryset.order_by('-user__date_joined')
    elif sort_by == 'experience':
        queryset = queryset.order_by('-years_experience', '-user__date_joined')
    elif sort_by == 'rating':
        queryset = queryset.order_by('-rating', '-user__date_joined')
    elif sort_by == 'date_registered':
        queryset = queryset.order_by('-user__date_joined')
    elif sort_by == 'age':
        queryset = queryset.order_by('age', '-user__date_joined')
    else:
        queryset = queryset.order_by('-user__date_joined')  # Default ordering

    # Calculate total results count before pagination
    total_results = queryset.count()

    # Apply pagination
    page = request.query_params.get('page', 1)
    per_page = request.query_params.get('per_page', 20)

    try:
        per_page = int(per_page)
        per_page = min(per_page, 100)  # Limit maximum results per page
    except ValueError:
        per_page = 20

    if per_page < 1:
        per_page = 20

    paginator = Paginator(queryset, per_page)

    try:
        page_obj = paginator.page(page)
    except:
        # Invalid page number, return first page
        page_obj = paginator.page(1)

    # Prepare response data
    results = []
    for worker_profile in page_obj:
        results.append({
            'id': worker_profile.id,
            'user_id': worker_profile.user.id,
            'full_name': worker_profile.full_name,
            'age': worker_profile.age,
            'place_of_birth': worker_profile.place_of_birth,
            'region_of_origin': worker_profile.region_of_origin,
            'current_location': worker_profile.current_location,
            'languages': worker_profile.languages,
            'education_level': worker_profile.education_level,
            'religion': worker_profile.religion,
            'working_time': worker_profile.working_time,
            'skills': worker_profile.skills,
            'years_experience': worker_profile.years_experience,
            'rating': float(worker_profile.rating),
            'is_approved': worker_profile.is_approved,
            'profile_photo_url': worker_profile.profile_photo_thumbnail.url if worker_profile.profile_photo else None,
            'user_verified': worker_profile.user.is_verified,
            'date_registered': worker_profile.user.date_joined.isoformat(),
        })

    response_data = {
        'count': total_results,
        'next': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'per_page': per_page,
        'results': results,
    }

    # Cache the results for 15 minutes
    cache.set(cache_key, response_data, 900) # 15 minutes = 900 seconds

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_filters(request):
    """
    Get available filter options for the search UI
    """
    cache_key = "search_filters"
    cached_filters = cache.get(cache_key)
    if cached_filters:
        return Response(cached_filters, status=status.HTTP_200_OK)

    # Get unique values for different filter fields
    regions = Region.objects.values_list('name', flat=True)
    skills = Skill.objects.values_list('name', flat=True)
    languages = Language.objects.values_list('name', flat=True)
    education_levels = EducationLevel.objects.values_list('name', flat=True)
    religions = Religion.objects.values_list('name', flat=True)
    working_times = ['full_time', 'part_time', 'live_in']  # Using hardcoded values from model choices
    
    # Get min and max experience from existing profiles
    min_experience = WorkerProfile.objects.aggregate(min_exp=Min('years_experience'))['min_exp'] or 0
    max_experience = WorkerProfile.objects.aggregate(max_exp=Max('years_experience'))['max_exp'] or 20
    
    # Get min and max age
    min_age = WorkerProfile.objects.aggregate(min_age=Min('age'))['min_age'] or 18
    max_age = WorkerProfile.objects.aggregate(max_age=Max('age'))['max_age'] or 65
    
    # Get min and max rating
    min_rating = float(WorkerProfile.objects.aggregate(min_rating=Min('rating'))['min_rating'] or 0.0)
    max_rating = float(WorkerProfile.objects.aggregate(max_rating=Max('rating'))['max_rating'] or 5.0)
    
    response_data = {
        'regions': list(regions),
        'skills': list(skills),
        'languages': list(languages),
        'education_levels': list(education_levels),
        'religions': list(religions),
        'working_times': working_times,
        'experience_range': {
            'min': min_experience,
            'max': max_experience,
        },
        'age_range': {
            'min': min_age,
            'max': max_age,
        },
        'rating_range': {
            'min': min_rating,
            'max': max_rating,
        }
    }
    cache.set(cache_key, response_data, 60 * 60 * 24) # 24 hours
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_worker_profile(request):
    """
    Get, update, or partially update the authenticated worker's profile
    """
    try:
        worker_profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        # Get worker profile
        from .serializers import WorkerProfileSerializer
        serializer = WorkerProfileSerializer(worker_profile)
        response_data = serializer.data
        response_data['profile_completeness'] = worker_profile.get_profile_completeness()
        return Response(response_data)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update worker profile
        from .serializers import WorkerProfileUpdateSerializer
        partial = request.method == 'PATCH'
        serializer = WorkerProfileUpdateSerializer(
            worker_profile, 
            data=request.data, 
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data
            response_data['profile_completeness'] = worker_profile.get_profile_completeness()
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_worker_profile(request, worker_id):
    """
    Get a specific worker's profile by ID (for employers/admins to view worker profiles)
    """
    try:
        worker_profile = WorkerProfile.objects.select_related('user').get(id=worker_id)
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions - only allow if user is admin, or same user, or has proper access
    user = request.user
    if (user.id != worker_profile.user.id and 
        user.user_type != 'admin' and 
        user.user_type != 'employer'):
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from .serializers import WorkerProfileSerializer
    serializer = WorkerProfileSerializer(worker_profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_worker_profile(request):
    """
    Create a worker profile for the authenticated user
    """
    # Check if user already has a worker profile
    if hasattr(request.user, 'worker_profile'):
        return Response(
            {'error': 'Worker profile already exists for this user'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # The user can only create a profile for themselves
    if request.user.user_type != 'worker':
        return Response(
            {'error': 'Only users with worker type can create worker profiles'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from .serializers import WorkerProfileCreateSerializer
    serializer = WorkerProfileCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Manually assign the user since it's not passed in the data
        worker_profile = serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_worker_profile(request, worker_id):
    """
    Approve a worker profile (admin only)
    """
    if request.user.user_type != 'admin':
        return Response(
            {'error': 'Permission denied. Admin access required.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        worker_profile = WorkerProfile.objects.get(id=worker_id)
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
    
    from .serializers import WorkerProfileSerializer
    serializer = WorkerProfileSerializer(worker_profile)
    return Response({
        'message': 'Worker profile approved successfully',
        'worker_profile': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_worker_profile_photo(request):
    """
    Update worker's profile photo
    """
    try:
        worker_profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'profile_photo' not in request.FILES:
        return Response(
            {'error': 'No profile photo provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from users.file_security import validate_file_type, validate_file_size, validate_image_dimensions
    from .serializers import WorkerProfilePhotoUpdateSerializer
    
    # Get the uploaded file
    profile_photo = request.FILES['profile_photo']
    
    # Validate the file
    try:
        allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png']
        validate_file_type(profile_photo, allowed_image_types)
    except Exception as e:
        return Response(
            {'error': f'Invalid file type: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (profiles limited to 5MB)
    try:
        validate_file_size(profile_photo, max_size_mb=5)
    except Exception as e:
        return Response(
            {'error': f'File too large: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate image dimensions
    try:
        validate_image_dimensions(profile_photo)
    except Exception as e:
        return Response(
            {'error': f'Invalid image dimensions: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update the profile photo 
    serializer = WorkerProfilePhotoUpdateSerializer(
        worker_profile, 
        data={'profile_photo': profile_photo}, 
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        from .serializers import WorkerProfileSerializer
        response_data = WorkerProfileSerializer(worker_profile).data
        response_data['profile_completeness'] = worker_profile.get_profile_completeness()
        return Response(response_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_worker_certification(request):
    """
    Upload worker's certification document
    """
    try:
        worker_profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        return Response(
            {'error': 'Worker profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'certification' not in request.FILES:
        return Response(
            {'error': 'No certification document provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    certification_document = request.FILES['certification']
    
    # Validate file type (allow images and PDFs for certifications)
    from users.file_security import validate_file_type, validate_file_size
    
    try:
        allowed_types = [
            'image/jpeg', 
            'image/jpg', 
            'image/png',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        validate_file_type(certification_document, allowed_types)
    except Exception as e:
        return Response(
            {'error': f'Invalid file type: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (certifications limited to 10MB)
    try:
        validate_file_size(certification_document, max_size_mb=10)
    except Exception as e:
        return Response(
            {'error': f'File too large: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update the certification document
    worker_profile.certifications = certification_document
    worker_profile.save()
    
    from .serializers import WorkerProfileSerializer
    response_data = WorkerProfileSerializer(worker_profile).data
    response_data['profile_completeness'] = worker_profile.get_profile_completeness()
    return Response(response_data)