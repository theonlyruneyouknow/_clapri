# File: leads/urls.py
# Location: C:\git\_clapri\leads\urls.py

from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.LeadListView.as_view(), name='lead_list'),
    path('create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('<str:lead_id>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('<str:lead_id>/note/', views.LeadNoteView.as_view(), name='lead_note'),
    path('<str:lead_id>/status/', views.LeadStatusUpdateView.as_view(), name='lead_status'),
]