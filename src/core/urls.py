"""
MEDIGEST Health — URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # CKEditor 5 file uploads
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # ── API v1 ──────────────────────────────────────────
    path('api/v1/', include('accounts.urls')),
    path('api/v1/', include('books.urls')),
    path('api/v1/', include('questions.urls')),
    path('api/v1/', include('flashcards.urls')),
    path('api/v1/', include('learning.urls')),
    path('api/v1/', include('certificates.urls')),
    path('api/v1/', include('webhooks.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
