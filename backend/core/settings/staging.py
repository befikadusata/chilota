"""
Staging settings for Ethiopian Domestic & Skilled Worker Platform
"""
from .base import *

# Override base settings for staging environment
DEBUG = False

# Additional staging-specific settings
# Use environment-specific database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
    }
}

# Email settings for staging
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Security settings for staging
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Additional staging settings
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())