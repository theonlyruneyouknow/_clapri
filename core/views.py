from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from django.contrib import messages
from urllib.parse import quote, urlencode
from utils.auth import oauth, login_required, get_auth0_user
from django.conf import settings
import logging
import secrets

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context

def login(request):
    # Generate a random state parameter
    state = secrets.token_urlsafe(32)
    request.session['auth_state'] = state
    
    # Store the return URL if provided
    return_to = request.GET.get('returnTo', '/')
    request.session['return_to'] = return_to

    logger.debug(f"Generated state: {state}")
    logger.debug(f"Return URL: {return_to}")
    
    # Prepare callback URL
    callback_url = request.build_absolute_uri(reverse('core:callback'))
    
    return oauth.auth0.authorize_redirect(
        request,
        callback_url,
        state=state,
        audience=settings.AUTH0_AUDIENCE
    )

def callback(request):
    try:
        # Verify state
        stored_state = request.session.get('auth_state')
        request_state = request.GET.get('state')
        
        logger.debug(f"Stored state: {stored_state}")
        logger.debug(f"Request state: {request_state}")

        if not stored_state or stored_state != request_state:
            logger.error("State mismatch")
            messages.error(request, "Authentication failed: state mismatch")
            return redirect('core:home')

        # Clear the stored state
        del request.session['auth_state']

        # Get the token
        token = oauth.auth0.authorize_access_token(request)
        userinfo = token.get('userinfo')
        
        if not userinfo:
            logger.error("No user info in token")
            messages.error(request, "Failed to get user information")
            return redirect('core:home')

        # Store user info in session
        request.session['user'] = userinfo
        
        # Get the return URL and remove it from session
        return_to = request.session.pop('return_to', '/')
        
        messages.success(request, f"Welcome, {userinfo.get('name', 'User')}!")
        return redirect(return_to)

    except Exception as e:
        logger.exception("Callback error")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('core:home')

def logout(request):
    # Clear the session
    request.session.flush()
    
    # Construct logout URL
    params = {
        'returnTo': request.build_absolute_uri('/'),
        'client_id': settings.AUTH0_CLIENT_ID
    }
    logout_url = f"https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode(params)}"
    
    return redirect(logout_url)