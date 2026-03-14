from django.contrib import admin

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import (
    UserTopicProgress, UserHighlight, UserNote, UserBookmark,
    UserLearningPlanTopic, UserStudySession, RecentActivity,
)


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(ModelAdmin):
    """Read-only admin for viewing user topic progress."""

    list_display = (
        'user_email', 'topic_title', 'book_name', 'completion_badge',
        'tasks_display', 'reading_time_display', 'updated_at',
    )
    list_filter = ('is_completed', 'topic__specialty__book', 'topic__specialty')
    search_fields = ('user__email', 'topic__title')
    list_per_page = 50
    ordering = ('-updated_at',)

    def has_add_permission(self, request):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Topic', ordering='topic__title')
    def topic_title(self, obj):
        return obj.topic.title

    @display(description='Book')
    def book_name(self, obj):
        return obj.topic.specialty.book.title

    @display(
        description='Status',
        label={
            True: 'success',
            False: 'warning',
        },
    )
    def completion_badge(self, obj):
        if obj.is_completed:
            return True, "✓ Completed"
        return False, "○ In Progress"

    @display(description='Tasks')
    def tasks_display(self, obj):
        if total == 0:
            return '—'
        return f'{obj.tasks_completed}/{total}'

    @display(description='Reading Time')
    def reading_time_display(self, obj):
        minutes = obj.reading_time_seconds // 60
        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f'{hours}h {mins}m'
        return f'{minutes}m'


@admin.register(UserHighlight)
class UserHighlightAdmin(ModelAdmin):
    """Read-only admin for viewing user highlights."""

    list_display = ('user_email', 'topic_title', 'text_preview', 'color_badge', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('user__email', 'highlighted_text', 'topic__title')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title

    @display(description='Highlighted Text')
    def text_preview(self, obj):
        return obj.highlighted_text[:80] + '...' if len(obj.highlighted_text) > 80 else obj.highlighted_text

    @display(
        description='Color',
        label={
            'yellow': 'warning',
            'green': 'success',
            'blue': 'info',
            'pink': 'danger',
            'orange': 'warning',
        },
    )
    def color_badge(self, obj):
        return obj.color, obj.color.title()


@admin.register(UserNote)
class UserNoteAdmin(ModelAdmin):
    """Read-only admin for viewing user notes."""

    list_display = ('user_email', 'topic_title', 'note_preview', 'has_highlight', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'content', 'topic__title')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title

    @display(description='Note')
    def note_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content

    @display(description='Linked to Highlight', boolean=True)
    def has_highlight(self, obj):
        return obj.highlight is not None


@admin.register(UserBookmark)
class UserBookmarkAdmin(ModelAdmin):
    """Read-only admin for viewing user bookmarks."""

    list_display = ('user_email', 'topic_title', 'label', 'section_anchor', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'topic__title', 'label')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title


@admin.register(UserLearningPlanTopic)
class UserLearningPlanTopicAdmin(ModelAdmin):
    """Read-only admin for viewing user learning plan topics."""

    list_display = ('user_email', 'topic_title', 'book_name', 'added_at')
    list_filter = ('added_at', 'topic__specialty__book')
    search_fields = ('user__email', 'topic__title')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title

    @display(description='Book')
    def book_name(self, obj):
        return obj.topic.specialty.book.title


@admin.register(UserStudySession)
class UserStudySessionAdmin(ModelAdmin):
    """Read-only admin for viewing study sessions."""

    list_display = ('user_email', 'session_type_badge', 'duration_display', 'started_at')
    list_filter = ('session_type', 'started_at')
    search_fields = ('user__email',)
    list_per_page = 50
    ordering = ('-started_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(
        description='Type',
        label={
            'reading': 'info',
            'quiz': 'warning',
            'flashcard': 'success',
            'board_basics': 'primary',
            'core': 'danger',
        },
    )
    def session_type_badge(self, obj):
        return obj.session_type, obj.get_session_type_display()

    @display(description='Duration')
    def duration_display(self, obj):
        minutes = obj.duration_seconds // 60
        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f'{hours}h {mins}m'
        return f'{minutes}m'


@admin.register(RecentActivity)
class RecentActivityAdmin(ModelAdmin):
    """Read-only admin for viewing recent activity."""

    list_display = ('user_email', 'activity_type_badge', 'title', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'title')
    list_per_page = 50
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(
        description='Type',
        label={
            'reading': 'info',
            'quiz': 'warning',
            'flashcard': 'success',
            'board_basics': 'primary',
            'core': 'danger',
            'learning_plan': 'info',
        },
    )
    def activity_type_badge(self, obj):
        return obj.activity_type, obj.get_activity_type_display()
