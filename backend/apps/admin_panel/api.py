"""
Admin panel API endpoints using Django Ninja
"""
from ninja import Router
from typing import List
from admin_panel.schemas import (
    AdminDashboardStatsSchema,
    WorkerApprovalSchema
)
from admin_panel.models import AdminAction
from workers.models import WorkerProfile
from workers.schemas import WorkerProfileOutSchema
from users.auth import JWTAuth
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator

router = Router()
User = get_user_model()


@router.get("/dashboard/stats/", response=AdminDashboardStatsSchema, auth=JWTAuth())
def get_dashboard_stats(request):
    """
    Get dashboard statistics for admin panel
    """
    # Only allow admin users
    if not request.auth.is_staff and not request.auth.is_superuser:
        return {"detail": "Permission denied"}, 403
    
    total_users = User.objects.count()
    total_workers = WorkerProfile.objects.count()
    active_jobs = 0  # Placeholder - would need to query jobs app
    verified_users = User.objects.filter(is_verified=True).count()
    
    stats = AdminDashboardStatsSchema(
        total_users=total_users,
        total_workers=total_workers,
        active_jobs=active_jobs,
        verified_users=verified_users
    )
    
    return stats


@router.get("/workers/", response=List[WorkerProfileOutSchema], auth=JWTAuth())
def list_workers_for_approval(request):
    """
    List all workers for approval/review
    """
    # Only allow admin users
    if not request.auth.is_staff and not request.auth.is_superuser:
        return {"detail": "Permission denied"}, 403

    workers = WorkerProfile.objects.all()
    # Return the queryset directly - Ninja will handle serialization
    return workers


@router.post("/workers/{worker_id}/approve/", auth=JWTAuth())
def approve_worker_profile(request, worker_id: int, data: WorkerApprovalSchema):
    """
    Approve or reject a worker profile
    """
    # Only allow admin users
    if not request.auth.is_staff and not request.auth.is_superuser:
        return {"detail": "Permission denied"}, 403
    
    try:
        worker_profile = WorkerProfile.objects.get(id=worker_id)
        worker_profile.is_approved = data.approved
        worker_profile.approval_notes = data.notes
        worker_profile.approved_by = request.auth
        worker_profile.save()
        
        # Log admin action
        AdminAction.objects.create(
            admin=request.auth,
            action_type='worker_approval',
            target_user=worker_profile.user,
            details=f"Worker profile {'approved' if data.approved else 'rejected'}: {data.notes}"
        )
        
        return {"success": True}
    except WorkerProfile.DoesNotExist:
        return {"detail": "Worker profile not found"}, 404