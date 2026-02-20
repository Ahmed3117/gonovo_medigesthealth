"""
MEDIGEST Health — URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Admin site customization
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    path('admin/', admin.site.urls),

    # CKEditor 5 file uploads
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # API endpoints (will be built out later)
    # path('api/auth/', include('accounts.urls')),
    # path('api/books/', include('books.urls')),
    # path('api/questions/', include('questions.urls')),
    # path('api/flashcards/', include('flashcards.urls')),
    # path('api/learning/', include('learning.urls')),
    # path('api/certificates/', include('certificates.urls')),
    # path('api/webhooks/', include('webhooks.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
