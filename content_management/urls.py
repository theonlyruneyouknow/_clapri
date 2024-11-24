# File: content_management/urls.py

from django.urls import path
from . import views

app_name = 'content_management'

urlpatterns = [
    path('', views.ContentListView.as_view(), name='content_list'),
    path('create/', views.ContentCreateView.as_view(), name='content_create'),
    path('edit/<str:content_id>/', views.ContentEditView.as_view(), name='content_edit'),
    path('duplicate/<str:content_id>/', views.ContentDuplicateView.as_view(), name='content_duplicate'),
    path('archive/<str:content_id>/', views.ContentArchiveView.as_view(), name='content_archive'),
    path('theme/create/', views.ThemeCreateView.as_view(), name='theme_create'),
    path('theme/list/', views.ThemeListView.as_view(), name='theme_list'),
]