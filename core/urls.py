# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),  # Add this line
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('callback/', views.callback, name='callback'),
]