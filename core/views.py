# File: core/views.py
# Location: C:\git\_clapri\core\views.py

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.urls import reverse
from django.contrib import messages
from urllib.parse import quote, urlencode
from utils.auth import oauth, login_required, get_auth0_user
from django.conf import settings
import logging
import secrets  # Add this import

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context
    
class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context    
    
# Add this class after your existing views

class ServicesView(TemplateView):
    template_name = 'core/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_auth0_user(self.request)
        return context    

def login(request):
    state = secrets.token_urlsafe(32)
    request.session['auth_state'] = state
    return_to = request.GET.get('returnTo', '/')
    request.session['return_to'] = return_to
    
    logger.debug(f"Generated state: {state}")
    logger.debug(f"Return URL: {return_to}")
    
    return oauth.auth0.authorize_redirect(
        request,
        request.build_absolute_uri(reverse('core:callback')),
        audience=settings.AUTH0_AUDIENCE
    )

def callback(request):
    try:
        token = oauth.auth0.authorize_access_token(request)
        userinfo = token.get('userinfo')
        
        if not userinfo:
            logger.error("No user info in token")
            messages.error(request, "Failed to get user information")
            return redirect('core:home')

        request.session['user'] = userinfo
        return_to = request.session.pop('return_to', '/')
        
        messages.success(request, f"Welcome, {userinfo.get('name', 'User')}!")
        return redirect(return_to)

    except Exception as e:
        logger.exception("Callback error")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('core:home')

def logout(request):
    request.session.clear()
    params = {
        'returnTo': request.build_absolute_uri('/'),
        'client_id': settings.AUTH0_CLIENT_ID
    }
    return redirect(f"https://{settings.AUTH0_DOMAIN}/v2/logout?{urlencode(params)}")