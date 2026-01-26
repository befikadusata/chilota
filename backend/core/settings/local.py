"""
Local development settings for Ethiopian Domestic & Skilled Worker Platform
"""
from .base import *

# Override base settings for local development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Additional local development settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable Django Debug Toolbar for local development
if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

# Media files for local development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')