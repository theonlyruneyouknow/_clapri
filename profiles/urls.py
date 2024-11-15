# File: profiles/urls.py

from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('edit/', views.ProfileView.as_view(), name='profile'),
    path('testimonial/create/', views.TestimonialCreateView.as_view(), name='testimonial_create'),
    path('testimonial/edit/<str:testimonial_id>/', views.TestimonialEditView.as_view(), name='testimonial_edit'),
]