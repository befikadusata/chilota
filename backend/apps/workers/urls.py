from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.advanced_worker_search, name='advanced_worker_search'),
    path('filters/', views.get_search_filters, name='get_search_filters'),
    path('', views.manage_worker_profile, name='manage_worker_profile'),
    path('create/', views.create_worker_profile, name='create_worker_profile'),
    path('<int:worker_id>/', views.get_worker_profile, name='get_worker_profile'),
    path('<int:worker_id>/approve/', views.approve_worker_profile, name='approve_worker_profile'),
    path('photo/', views.update_worker_profile_photo, name='update_worker_profile_photo'),
    path('certification/', views.update_worker_certification, name='update_worker_certification'),
]