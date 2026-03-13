from django.contrib import admin

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Flashcard, UserFlashcardProgress, UserCustomFlashcard


@admin.register(Flashcard)
class FlashcardAdmin(ModelAdmin):
    """
    Admin for managing system flashcards.
    Uses Unfold for premium styling.
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
            'fields': ('book', 'specialty', 'topic', 'display_order'),
        }),
        ('Cross-Module Link', {
            'fields': ('related_topic',),
            'classes': ('collapse',),
            'description': 'The topic linked via "Related Text →" on the answer side of the flashcard.',
        }),
        ('Settings', {
            'fields': ('is_active',),
        }),
    )

    @display(description='Front (Preview)')
    def front_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.front_text or '')
        return clean[:100] + '...' if len(clean) > 100 else clean

    @display(description='Specialty', ordering='specialty__name')
    def specialty_name(self, obj):
        return obj.specialty.name

    @display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'


@admin.register(UserFlashcardProgress)
class UserFlashcardProgressAdmin(ModelAdmin):
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

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Flashcard')
    def flashcard_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.flashcard.front_text or '')
        return clean[:60] + '...' if len(clean) > 60 else clean

    @display(
        description='Confidence',
        label={
            0: 'info',
            1: 'danger',
            2: 'warning',
            3: 'success',
            4: 'primary',
        },
    )
    def confidence_badge(self, obj):
        labels = {
            0: 'Not Reviewed',
            1: 'Not Confident',
            2: 'Somewhat',
            3: 'Confident',
            4: 'Very Confident',
        }
        label = labels.get(obj.confidence, '—')
        return obj.confidence, label


@admin.register(UserCustomFlashcard)
class UserCustomFlashcardAdmin(ModelAdmin):
    """Read-only admin for viewing user-created flashcards."""

    list_display = ('user_email', 'front_preview', 'topic_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'front_text', 'back_text')
    list_per_page = 25
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Front')
    def front_preview(self, obj):
        return obj.front_text[:80] + '...' if len(obj.front_text) > 80 else obj.front_text

    @display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'
