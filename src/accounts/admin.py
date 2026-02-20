from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for MEDIGEST User model.
    Provides a user-friendly interface for managing users and their access.
    """

    # ── List View ──
    list_display = (
        'email', 'full_name_display', 'role', 'purchased_books_display',
        'is_active', 'created_at_display',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'theme', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    list_per_page = 25
    list_editable = ('role', 'is_active')

    # ── Detail View ──
    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'profile_picture'),
        }),
        ('Role & Preferences', {
            'fields': ('role', 'theme', 'font_size', 'email_notifications'),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # ── Add User View ──
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    # ── Custom Columns ──
    @admin.display(description='Name', ordering='first_name')
    def full_name_display(self, obj):
        name = obj.get_full_name()
        return name if name else '—'

    @admin.display(description='Books')
    def purchased_books_display(self, obj):
        count = obj.purchased_books_count
        if count > 0:
            return format_html(
                '<span style="color: #059669; font-weight: 600;">{}</span>',
                count
            )
        return mark_safe('<span style="color: #9CA3AF;">0</span>')

    @admin.display(description='Joined', ordering='created_at')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
