from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    # path('content/', include('content_management.urls')),
    # path('profile/', include('profiles.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

