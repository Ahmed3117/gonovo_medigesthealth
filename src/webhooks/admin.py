from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """
    Read-only admin for viewing webhook logs.
    Provides clear visual indicators for status and signature validation.
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
        # Allow deletion for cleanup
        return True

    # ── Custom Columns ──
    @admin.display(description='Order ID')
    def order_id_display(self, obj):
        return obj.order_id or mark_safe('<span style="color:#9CA3AF;">—</span>')

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'received': ('#6B7280', '#F3F4F6'),
            'processing': ('#1D4ED8', '#DBEAFE'),
            'processed': ('#059669', '#D1FAE5'),
            'failed': ('#DC2626', '#FEE2E2'),
            'invalid_sig': ('#DC2626', '#FEE2E2'),
        }
        fg, bg = colors.get(obj.processing_status, ('#6B7280', '#F3F4F6'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, obj.get_processing_status_display()
        )

    @admin.display(description='Signature')
    def signature_badge(self, obj):
        if obj.signature_valid:
            return mark_safe(
                '<span style="color:#059669; font-weight:700;">✓ Valid</span>'
            )
        return mark_safe(
            '<span style="color:#DC2626; font-weight:700;">✗ Invalid</span>'
        )

    @admin.display(description='New User', boolean=True)
    def user_created_badge(self, obj):
        return obj.user_created

    @admin.display(description='Payload')
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
