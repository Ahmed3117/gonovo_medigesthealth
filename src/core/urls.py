"""
MEDIGEST Health — URL Configuration
"""
import sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

@csrf_exempt
def debug_migrate(request):
    """Temporary: run pending migrations and show DB status. Remove after use."""
    secret = request.GET.get('secret', '')
    if secret != 'medigest_migrate_2026':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('migrate', stdout=out, stderr=out)
        migrate_output = out.getvalue()

        out2 = StringIO()
        call_command('showmigrations', 'accounts', stdout=out2)
        show_output = out2.getvalue()

        # Check if accounts_passwordresetotp table exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE tablename='accounts_passwordresetotp';")
            table_exists = cursor.fetchone() is not None

        return JsonResponse({
            'status': 'ok',
            'migrate_output': migrate_output,
            'accounts_migrations': show_output,
            'passwordresetotp_table_exists': table_exists,
            'python_version': sys.version,
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'status': 'error',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


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
    # ── Temporary debug migration endpoint ──────────────
    path('api/v1/debug/migrate/', debug_migrate),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
