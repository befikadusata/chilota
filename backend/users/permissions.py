from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.user_type == 'admin'
        return False


class IsEmployerUser(permissions.BasePermission):
    """
    Custom permission to only allow employer users
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.user_type == 'employer'
        return False


class IsWorkerUser(permissions.BasePermission):
    """
    Custom permission to only allow worker users
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.user_type == 'worker'
        return False


class IsSameUserOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own profile
    or admins to access any profile
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user_type'):
            # If it's a user object
            user = obj
        else:
            # If it's another model with a user relation
            user = getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        
        if not user:
            return False
            
        # Admins can access any object
        if request.user.user_type == 'admin':
            return True
            
        # Users can access their own objects
        return user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins
    """
    def has_object_permission(self, request, view, obj):
        # Admins can access any object
        if request.user.user_type == 'admin':
            return True
            
        # Check if the object has a user field that matches the current user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False