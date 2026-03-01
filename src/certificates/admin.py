from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import CMEActivity, UserCMECredit, CMESubmission, UserCOREProgress, Certificate


@admin.register(CMEActivity)
class CMEActivityAdmin(ModelAdmin):
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

    @display(
        description='Type',
        label={
            'syllabus': 'info',
            'quiz': 'warning',
            'board_basics': 'success',
            'question': 'primary',
        },
    )
    def activity_type_badge(self, obj):
        return obj.activity_type, obj.get_activity_type_display()

    @display(description='Credits')
    def credits_display(self, obj):
        return obj.credits

    @display(description='Specialty')
    def specialty_name(self, obj):
        return obj.specialty.name if obj.specialty else '—'


@admin.register(UserCMECredit)
class UserCMECreditAdmin(ModelAdmin):
    """Admin for viewing/managing user CME credits."""

    list_display = ('user_email', 'activity_title', 'credits_earned', 'credit_year', 'status_badge', 'earned_at')
    list_filter = ('status', 'credit_year', 'earned_at')
    search_fields = ('user__email',)
    list_per_page = 25
    ordering = ('-earned_at',)

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Activity')
    def activity_title(self, obj):
        if obj.activity:
            return obj.activity.title
        return '—'

    @display(
        description='Status',
        label={
            'earned': 'warning',
            'submitted': 'info',
            'verified': 'success',
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()


@admin.register(CMESubmission)
class CMESubmissionAdmin(ModelAdmin):
    """Admin for viewing CME credit submissions."""

    list_display = ('user_email', 'accreditation_badge', 'credits_claimed', 'credit_year', 'status_badge', 'submitted_at')
    list_filter = ('accreditation_body', 'status', 'credit_year', 'submitted_at')
    search_fields = ('user__email',)
    list_per_page = 25
    ordering = ('-submitted_at',)

    def has_add_permission(self, request):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Accreditation')
    def accreditation_badge(self, obj):
        return obj.get_accreditation_body_display()

    @display(
        description='Status',
        label={
            'pending': 'warning',
            'submitted': 'info',
            'confirmed': 'success',
            'rejected': 'danger',
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_submission_status_display()


@admin.register(UserCOREProgress)
class UserCOREProgressAdmin(ModelAdmin):
    """Admin for viewing CORE badge progress."""

    list_display = (
        'user_email', 'specialty_name', 'badge_status_display',
        'progress_display', 'accuracy_display', 'core_quiz_unlocked',
    )
    list_filter = ('badge_status', 'core_quiz_unlocked', 'specialty__book')
    search_fields = ('user__email', 'specialty__name')
    list_per_page = 25
    ordering = ('specialty__name',)

    def has_add_permission(self, request):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Specialty')
    def specialty_name(self, obj):
        return obj.specialty.name

    @display(
        description='Badge',
        label={
            'pending': 'warning',
            'in_progress': 'info',
            'completed': 'success',
        },
    )
    def badge_status_display(self, obj):
        return obj.badge_status, obj.get_badge_status_display()

    @display(description='Progress')
    def progress_display(self, obj):
        return f'{obj.questions_answered} Qs answered'

    @display(description='Accuracy')
    def accuracy_display(self, obj):
        if obj.questions_answered == 0:
            return '—'
        pct = round((obj.questions_correct / obj.questions_answered) * 100, 1)
        return f'{pct}%'


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    """Admin for managing certificates."""

    list_display = ('user_email', 'title', 'type_badge', 'total_credits', 'credit_year', 'pdf_link', 'issued_at')
    list_filter = ('certificate_type', 'credit_year', 'issued_at')
    search_fields = ('user__email', 'title')
    list_per_page = 25
    ordering = ('-issued_at',)

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(
        description='Type',
        label={
            'core': 'primary',
            'cme': 'success',
            'exam': 'danger',
        },
    )
    def type_badge(self, obj):
        return obj.certificate_type, obj.get_certificate_type_display()

    @display(description='PDF')
    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" '
                'class="text-primary-600 hover:text-primary-800 font-medium">'
                '📄 Download</a>',
                obj.pdf_file.url
            )
        return '—'
