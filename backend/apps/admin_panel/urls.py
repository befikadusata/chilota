from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Worker profile management
    path('workers/approve/<int:worker_id>/', views.approve_worker_profile, name='approve-worker'),
    path('workers/reject/<int:worker_id>/', views.reject_worker_profile, name='reject-worker'),
    path('workers/pending/', views.get_pending_worker_profiles, name='pending-workers'),
    
    # User account management
    path('users/flag/<int:user_id>/', views.flag_user_account, name='flag-user'),
    path('users/suspend/<int:user_id>/', views.suspend_user_account, name='suspend-user'),
    path('users/', views.get_user_accounts, name='get-users'),
    
    # Job posting management
    path('jobs/approve/<int:job_id>/', views.approve_job_posting, name='approve-job'),
    path('jobs/reject/<int:job_id>/', views.reject_job_posting, name='reject-job'),
    path('jobs/pending/', views.get_pending_job_postings, name='pending-jobs'),
    
    # Analytics and reporting
    path('analytics/workers/', views.get_worker_statistics, name='worker-stats'),
    path('analytics/trends/', views.get_registration_trends, name='registration-trends'),
    path('analytics/platform/', views.get_platform_analytics, name='platform-analytics'),
    
    # Data export
    path('export/workers/', views.export_worker_data, name='export-workers'),
    path('export/jobs/', views.export_job_data, name='export-jobs'),
]