"""
URL configuration for Ethiopian Domestic & Skilled Worker Platform.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    1. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from api.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: JsonResponse({"status": "ok"}), name="health_check"),
    path("api/", api.urls),  # Django Ninja API
    # Keep legacy DRF endpoints for backward compatibility during transition
    path('api/auth/', include('users.urls')),
    path('api/workers/', include('apps.workers.urls')),
    path('api/employers/', include('apps.employers.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
