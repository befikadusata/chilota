"""
Authentication utilities for the users API
"""
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class JWTAuth(HttpBearer):
    """
    Custom JWT authentication for Ninja API
    """
    def authenticate(self, request, token):
        try:
            # Decode the JWT token
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            
            # Get the user from the database
            user = User.objects.get(id=user_id)
            return user
        except TokenError:
            # Token is invalid
            return None
        except User.DoesNotExist:
            # User doesn't exist
            return None