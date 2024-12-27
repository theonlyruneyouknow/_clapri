# File: utils/auth.py
# Location: C:\git\_clapri\utils\auth.py

from functools import wraps
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from authlib.integrations.django_client import OAuth
import logging

logger = logging.getLogger(__name__)

# Initialize OAuth
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    api_base_url=f"https://{settings.AUTH0_DOMAIN}",
    access_token_url=f"https://{settings.AUTH0_DOMAIN}/oauth/token",
    authorize_url=f"https://{settings.AUTH0_DOMAIN}/authorize",
    jwks_uri=f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json",
    client_kwargs={
        "scope": "openid profile email",
        "audience": settings.AUTH0_AUDIENCE
    },
)

def login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        if not request.session.get('user'):
            return redirect(f'/login?returnTo={request.path}')
        return f(request, *args, **kwargs)
    return decorated_function

def get_auth0_user(request):
    """Get Auth0 user from session"""
    return request.session.get('user')

def is_admin(user):
    """Check if user has admin privileges"""
    if not user:
        return False
        
    # Check all possible locations for admin flag
    return any([
        user.get('is_admin'),
        user.get('/app_metadata', {}).get('is_admin'),
        user.get('app_metadata', {}).get('is_admin'),
        user.get('/user_metadata', {}).get('is_admin'),
        user.get('user_metadata', {}).get('is_admin')
    ])

def admin_required(f):
    """Decorator for views that require admin access"""
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        user = get_auth0_user(request)
        if not user or not is_admin(user):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('core:home')
        return f(request, *args, **kwargs)
    return decorated_function