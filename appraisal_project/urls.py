from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('admin/', admin.site.urls),
    path('content/', include('content_management.urls', namespace='content_management')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
