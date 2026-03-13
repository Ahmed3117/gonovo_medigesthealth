"""
MEDIGEST Health — URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.admin_views import ImportDemoDataView, UploadFigmaDataView

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Admin utility views ──────────────────────────────
    path('admin/import-demo-data/', ImportDemoDataView.as_view(), name='admin_import_demo_data'),
    path('upload-test-data/', UploadFigmaDataView.as_view(), name='upload_test_data'),

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
