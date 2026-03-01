from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(ModelAdmin):
    """
    Read-only admin for viewing webhook logs.
    Uses Unfold labels for clear status indicators.
    """

    list_display = (
        'order_id_display', 'customer_email', 'status_badge', 'signature_badge',
        'user_created_badge', 'books_granted', 'received_at',
    )
    list_filter = ('processing_status', 'signature_valid', 'user_created', 'received_at')
    search_fields = ('order_id', 'customer_email', 'error_message')
    list_per_page = 25
    ordering = ('-received_at',)
    readonly_fields = (
        'order_id', 'customer_email', 'payload_pretty', 'signature_valid',
        'processing_status', 'error_message', 'ip_address',
        'user_created', 'books_granted', 'received_at', 'processed_at',
    )

    fieldsets = (
        ('Overview', {
            'fields': ('order_id', 'customer_email', 'processing_status', 'signature_valid'),
        }),
        ('Results', {
            'fields': ('user_created', 'books_granted'),
        }),
        ('Request Details', {
            'fields': ('ip_address', 'received_at', 'processed_at'),
        }),
        ('Payload', {
            'fields': ('payload_pretty',),
            'classes': ('collapse',),
        }),
        ('Errors', {
            'fields': ('error_message',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    # ── Custom Columns ──
    @display(description='Order ID')
    def order_id_display(self, obj):
        return obj.order_id or '—'

    @display(
        description='Status',
        label={
            'received': 'info',
            'processing': 'warning',
            'processed': 'success',
            'failed': 'danger',
            'invalid_sig': 'danger',
        },
    )
    def status_badge(self, obj):
        return obj.processing_status, obj.get_processing_status_display()

    @display(
        description='Signature',
        label={
            True: 'success',
            False: 'danger',
        },
    )
    def signature_badge(self, obj):
        if obj.signature_valid:
            return True, "✓ Valid"
        return False, "✗ Invalid"

    @display(description='New User', boolean=True)
    def user_created_badge(self, obj):
        return obj.user_created

    @display(description='Payload')
    def payload_pretty(self, obj):
        import json
        try:
            pretty = json.dumps(obj.payload_json, indent=2, ensure_ascii=False)
            return format_html(
                '<pre style="background:#1F2937; color:#E5E7EB; padding:16px; '
                'border-radius:8px; font-size:12px; max-height:400px; '
                'overflow:auto; white-space:pre-wrap;">{}</pre>',
                pretty
            )
        except Exception:
            return str(obj.payload_json)
