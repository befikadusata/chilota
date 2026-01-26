"""
Main API configuration using Django Ninja
"""
from ninja import NinjaAPI
from django.conf import settings
from .v1.endpoints.user_endpoints import router as users_router
from .v1.endpoints.worker_endpoints import router as workers_router
from .v1.endpoints.employer_endpoints import router as employers_router
from .v1.endpoints.admin_endpoints import router as admin_router
from .v1.endpoints.notification_endpoints import router as notifications_router

# Create the main API instance
api = NinjaAPI(
    title="Ethiopian Domestic & Skilled Worker Platform API",
    version="1.0.0",
    description="API for connecting households and businesses with domestic and skilled workers across Ethiopia",
    docs_url="/api/docs/",
)

# Add routers for different modules
api.add_router("/auth/", users_router, tags=["Authentication"])
api.add_router("/workers/", workers_router, tags=["Workers"])
api.add_router("/employers/", employers_router, tags=["Employers"])
api.add_router("/admin/", admin_router, tags=["Admin"])
api.add_router("/notifications/", notifications_router, tags=["Notifications"])

__all__ = ["api"]