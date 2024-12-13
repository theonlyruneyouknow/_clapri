# File: core/urls.py
# Location: C:\git\_clapri\core\urls.py

from django.urls import path, include
from . import views
from . import admin_views
from .views import AppraisalReportView, AppraisalListView

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    
    # Lead management
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<str:id>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<str:id>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
]