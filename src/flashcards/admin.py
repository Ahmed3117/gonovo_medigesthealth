from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Flashcard, UserFlashcardProgress, UserCustomFlashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    """
    Admin for managing system flashcards.
    Shows front preview, specialty, topic, and status.
    """

    list_display = (
        'front_preview', 'specialty_name', 'topic_name', 'is_active', 'updated_at',
    )
    list_display_links = ('front_preview',)
    list_filter = ('is_active', 'specialty__book', 'specialty')
    list_editable = ('is_active',)
    search_fields = ('front_text', 'back_text', 'specialty__name', 'topic__title')
    list_per_page = 25
    ordering = ('specialty__name', '-created_at')

    fieldsets = (
        ('Card Content', {
            'fields': ('front_text', 'back_text'),
            'description': 'Enter the front (question) and back (answer) content for this flashcard.',
        }),
        ('Classification', {
            'fields': ('specialty', 'topic'),
        }),
        ('Settings', {
            'fields': ('is_active',),
        }),
    )

    @admin.display(description='Front (Preview)')
    def front_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.front_text or '')
        return clean[:100] + '...' if len(clean) > 100 else clean

    @admin.display(description='Specialty', ordering='specialty__name')
    def specialty_name(self, obj):
        return obj.specialty.name

    @admin.display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'


@admin.register(UserFlashcardProgress)
class UserFlashcardProgressAdmin(admin.ModelAdmin):
    """Read-only admin for viewing flashcard progress."""

    list_display = ('user_email', 'flashcard_preview', 'confidence_badge', 'times_reviewed', 'last_reviewed_at')
    list_filter = ('confidence', 'last_reviewed_at')
    search_fields = ('user__email',)
    list_per_page = 50
    ordering = ('-last_reviewed_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Flashcard')
    def flashcard_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.flashcard.front_text or '')
        return clean[:60] + '...' if len(clean) > 60 else clean

    @admin.display(description='Confidence')
    def confidence_badge(self, obj):
        colors = {
            0: ('#6B7280', '#F3F4F6', 'Not Reviewed'),
            1: ('#DC2626', '#FEE2E2', 'Not Confident'),
            2: ('#D97706', '#FEF3C7', 'Somewhat'),
            3: ('#059669', '#D1FAE5', 'Confident'),
            4: ('#1D4ED8', '#DBEAFE', 'Very Confident'),
        }
        fg, bg, label = colors.get(obj.confidence, ('#6B7280', '#F3F4F6', '—'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, label
        )


@admin.register(UserCustomFlashcard)
class UserCustomFlashcardAdmin(admin.ModelAdmin):
    """Read-only admin for viewing user-created flashcards."""

    list_display = ('user_email', 'front_preview', 'topic_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'front_text', 'back_text')
    list_per_page = 25
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Front')
    def front_preview(self, obj):
        return obj.front_text[:80] + '...' if len(obj.front_text) > 80 else obj.front_text

    @admin.display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'
