from django.urls import path
from . import views

urlpatterns = [
    # Job postings
    path('jobs/', views.job_postings_list, name='job_postings_list'),
    path('jobs/<int:job_id>/', views.job_posting_detail, name='job_posting_detail'),
    
    # Job applications
    path('jobs/<int:job_id>/applications/', views.get_job_applications, name='get_job_applications'),
    path('jobs/<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    
    # Shortlist management
    path('shortlist/', views.shortlist_management, name='shortlist_management'),
    path('jobs/<int:job_id>/shortlist/<int:worker_id>/', views.remove_from_shortlist, name='remove_from_shortlist'),
    
    # Employer profile
    path('profile/', views.get_employer_profile, name='get_employer_profile'),
]