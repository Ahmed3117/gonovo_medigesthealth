from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import CMEActivity, UserCMECredit, Certificate


@admin.register(CMEActivity)
class CMEActivityAdmin(admin.ModelAdmin):
    """Admin for managing CME activities."""

    list_display = ('title', 'activity_type_badge', 'credits_display', 'specialty_name', 'is_active')
    list_filter = ('activity_type', 'is_active', 'specialty__book')
    list_editable = ('is_active',)
    search_fields = ('title', 'description')
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'activity_type', 'credits', 'specialty', 'is_active'),
        }),
    )

    @admin.display(description='Type')
    def activity_type_badge(self, obj):
        icons = {
            'syllabus': ('📖', '#DBEAFE', '#1D4ED8'),
            'quiz': ('🎯', '#FEF3C7', '#D97706'),
            'board_basics': ('📋', '#D1FAE5', '#059669'),
        }
        icon, bg, fg = icons.get(obj.activity_type, ('📌', '#F3F4F6', '#6B7280'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{} {}</span>',
            bg, fg, icon, obj.get_activity_type_display()
        )

    @admin.display(description='Credits')
    def credits_display(self, obj):
        return format_html(
            '<span style="font-weight:700; color:#059669;">{}</span>', obj.credits
        )

    @admin.display(description='Specialty')
    def specialty_name(self, obj):
        return obj.specialty.name if obj.specialty else '—'


@admin.register(UserCMECredit)
class UserCMECreditAdmin(admin.ModelAdmin):
    """Admin for viewing/managing user CME credits."""

    list_display = ('user_email', 'activity_title', 'credits_earned', 'status_badge', 'earned_at')
    list_filter = ('status', 'earned_at', 'activity__activity_type')
    search_fields = ('user__email', 'activity__title')
    list_per_page = 25
    ordering = ('-earned_at',)

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Activity')
    def activity_title(self, obj):
        return obj.activity.title

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'earned': ('#D97706', '#FEF3C7'),
            'submitted': ('#1D4ED8', '#DBEAFE'),
            'verified': ('#059669', '#D1FAE5'),
        }
        fg, bg = colors.get(obj.status, ('#6B7280', '#F3F4F6'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display()
        )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin for managing certificates."""

    list_display = ('user_email', 'title', 'type_badge', 'total_credits', 'pdf_link', 'issued_at')
    list_filter = ('certificate_type', 'issued_at')
    search_fields = ('user__email', 'title')
    list_per_page = 25
    ordering = ('-issued_at',)

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Type')
    def type_badge(self, obj):
        colors = {
            'core': ('#7C3AED', '#EDE9FE'),
            'cme': ('#059669', '#D1FAE5'),
            'exam': ('#DC2626', '#FEE2E2'),
        }
        fg, bg = colors.get(obj.certificate_type, ('#6B7280', '#F3F4F6'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, obj.get_certificate_type_display()
        )

    @admin.display(description='PDF')
    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" style="color:#1D4ED8;">📄 Download</a>',
                obj.pdf_file.url
            )
        return mark_safe('<span style="color:#9CA3AF;">Not generated</span>')
