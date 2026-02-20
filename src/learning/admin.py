from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import UserTopicProgress, UserHighlight, UserNote, RecentActivity


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    """Read-only admin for viewing user topic progress."""

    list_display = (
        'user_email', 'topic_title', 'book_name', 'completion_badge',
        'reading_time_display', 'updated_at',
    )
    list_filter = ('is_completed', 'topic__specialty__book', 'topic__specialty')
    search_fields = ('user__email', 'topic__title')
    list_per_page = 50
    ordering = ('-updated_at',)

    def has_add_permission(self, request):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Topic', ordering='topic__title')
    def topic_title(self, obj):
        return obj.topic.title

    @admin.display(description='Book')
    def book_name(self, obj):
        return obj.topic.specialty.book.title

    @admin.display(description='Status')
    def completion_badge(self, obj):
        if obj.is_completed:
            return mark_safe(
                '<span style="color:#059669; font-weight:700;">✓ Completed</span>'
            )
        return mark_safe(
            '<span style="color:#D97706;">○ In Progress</span>'
        )

    @admin.display(description='Reading Time')
    def reading_time_display(self, obj):
        minutes = obj.reading_time_seconds // 60
        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f'{hours}h {mins}m'
        return f'{minutes}m'


@admin.register(UserHighlight)
class UserHighlightAdmin(admin.ModelAdmin):
    """Read-only admin for viewing user highlights."""

    list_display = ('user_email', 'topic_title', 'text_preview', 'color_badge', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('user__email', 'highlighted_text', 'topic__title')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title

    @admin.display(description='Highlighted Text')
    def text_preview(self, obj):
        return obj.highlighted_text[:80] + '...' if len(obj.highlighted_text) > 80 else obj.highlighted_text

    @admin.display(description='Color')
    def color_badge(self, obj):
        color_map = {
            'yellow': '#FCD34D',
            'green': '#6EE7B7',
            'blue': '#93C5FD',
            'pink': '#F9A8D4',
            'orange': '#FDBA74',
        }
        hex_color = color_map.get(obj.color, '#E5E7EB')
        return format_html(
            '<span style="background:{}; padding:2px 12px; border-radius:8px; '
            'font-size:11px;">{}</span>',
            hex_color, obj.color.title()
        )


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    """Read-only admin for viewing user notes."""

    list_display = ('user_email', 'topic_title', 'note_preview', 'has_highlight', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'content', 'topic__title')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Topic')
    def topic_title(self, obj):
        return obj.topic.title

    @admin.display(description='Note')
    def note_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content

    @admin.display(description='Linked to Highlight', boolean=True)
    def has_highlight(self, obj):
        return obj.highlight is not None


@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
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

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Type')
    def activity_type_badge(self, obj):
        icons = {
            'reading': ('📖', '#DBEAFE', '#1D4ED8'),
            'quiz': ('🎯', '#FEF3C7', '#D97706'),
            'flashcard': ('⚡', '#D1FAE5', '#059669'),
        }
        icon, bg, fg = icons.get(obj.activity_type, ('📌', '#F3F4F6', '#6B7280'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{} {}</span>',
            bg, fg, icon, obj.get_activity_type_display()
        )
