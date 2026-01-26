from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView  # This is for logout, though JWT tokens can't really be blacklisted unless using an extra package
)
from . import views

urlpatterns = [
    # JWT authentication
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', views.logout_view, name='token_blacklist'),  # Using custom logout view
    
    # User registration and profile
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('profile/', views.get_user_profile, name='user_profile'),
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
    
    # File upload endpoints
    path('upload/profile-photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('upload/certification/', views.upload_certification, name='upload_certification'),
    path('files/', views.get_user_files, name='get_user_files'),
    path('files/<int:file_id>/download/', views.download_file, name='download_file'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    
    # Password reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
]