# utils/auth_middleware.py
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from urllib.parse import urlencode
import jwt
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

class Auth0Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that don't require authentication
        public_paths = [
            '/login/',
            '/logout/',
            '/callback/',
            '/',
            '/about/',
            '/services/',
            '/contact/',
            '/static/',
        ]

        # Check if the current path is public
        if any(request.path.startswith(path) for path in public_paths):
            return self.get_response(request)

        # Check if user is authenticated
        if 'user' not in request.session or not request.session['user']:
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f'/login?returnTo={request.path}')

        try:
            # Validate the user's JWT token
            user_token = request.session['user']['access_token']
            payload = jwt.decode(user_token, key=settings.AUTH0_CLIENT_SECRET, algorithms=['HS256'])
            # You can perform additional validation checks here, such as checking the token expiration
        except (KeyError, InvalidTokenError):
            # If the token is invalid, clear the user session and redirect to the login page
            request.session.pop('user', None)
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f'/login?returnTo={request.path}')

        return self.get_response(request)

class UserAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'user' in request.session and request.session['user']:
            user = request.session['user']
            
            # Add user permissions to request
            request.user_permissions = {
                'is_admin': user.get('app_metadata', {}).get('is_admin', False),
                'is_editor': user.get('app_metadata', {}).get('is_editor', False),
                'can_edit_content': user.get('app_metadata', {}).get('can_edit_content', False),
            }
            
        return self.get_response(request)