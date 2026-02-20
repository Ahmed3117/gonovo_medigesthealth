from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Question, UserQuestionAttempt, QuizSession


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin for managing MCQ questions.
    Shows question preview, correct answer, difficulty, and specialty.
    """

    list_display = (
        'question_preview', 'specialty_name', 'topic_name',
        'correct_answer_badge', 'difficulty_badge', 'is_active', 'updated_at',
    )
    list_display_links = ('question_preview',)
    list_filter = ('difficulty', 'is_active', 'specialty__book', 'specialty')
    list_editable = ('is_active',)
    search_fields = ('question_text', 'explanation', 'specialty__name', 'topic__title')
    list_per_page = 25
    ordering = ('specialty__name', '-created_at')

    fieldsets = (
        ('Question', {
            'fields': ('specialty', 'topic', 'question_text', 'question_image'),
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'correct_answer'),
            'description': 'Enter the text for each option. Mark the correct answer below.',
        }),
        ('Explanation', {
            'fields': ('explanation', 'educational_objective'),
            'classes': ('wide',),
        }),
        ('Settings', {
            'fields': ('difficulty', 'is_active'),
        }),
    )

    @admin.display(description='Question', ordering='question_text')
    def question_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.question_text or '')
        preview = clean[:100] + '...' if len(clean) > 100 else clean
        return preview

    @admin.display(description='Specialty', ordering='specialty__name')
    def specialty_name(self, obj):
        return obj.specialty.name

    @admin.display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'

    @admin.display(description='Answer')
    def correct_answer_badge(self, obj):
        return format_html(
            '<span style="background:#D1FAE5; color:#059669; padding:2px 10px; '
            'border-radius:10px; font-size:12px; font-weight:700;">{}</span>',
            obj.correct_answer
        )

    @admin.display(description='Difficulty')
    def difficulty_badge(self, obj):
        colors = {
            'easy': ('#059669', '#D1FAE5'),
            'medium': ('#D97706', '#FEF3C7'),
            'hard': ('#DC2626', '#FEE2E2'),
        }
        fg, bg = colors.get(obj.difficulty, ('#6B7280', '#F3F4F6'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, obj.get_difficulty_display()
        )


@admin.register(UserQuestionAttempt)
class UserQuestionAttemptAdmin(admin.ModelAdmin):
    """Read-only admin for viewing question attempt history."""

    list_display = ('user_email', 'question_preview', 'selected_answer', 'result_badge', 'is_saved', 'attempted_at')
    list_filter = ('is_correct', 'is_saved', 'attempted_at')
    search_fields = ('user__email', 'question__question_text')
    list_per_page = 50
    ordering = ('-attempted_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Question')
    def question_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.question.question_text or '')
        return clean[:60] + '...' if len(clean) > 60 else clean

    @admin.display(description='Result')
    def result_badge(self, obj):
        if obj.is_correct:
            return mark_safe(
                '<span style="color:#059669; font-weight:700;">✓ Correct</span>'
            )
        return mark_safe(
            '<span style="color:#DC2626; font-weight:700;">✗ Wrong</span>'
        )


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    """Read-only admin for viewing quiz sessions."""

    list_display = ('user_email', 'mode_badge', 'score_display', 'total_questions', 'is_completed', 'started_at')
    list_filter = ('mode', 'is_completed', 'started_at')
    search_fields = ('user__email',)
    list_per_page = 25
    ordering = ('-started_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Mode')
    def mode_badge(self, obj):
        if obj.mode == 'exam':
            return mark_safe(
                '<span style="background:#FEE2E2; color:#DC2626; padding:2px 8px; '
                'border-radius:10px; font-size:11px; font-weight:600;">🎯 Exam</span>'
            )
        return mark_safe(
            '<span style="background:#DBEAFE; color:#1D4ED8; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">📝 Practice</span>'
        )

    @admin.display(description='Score')
    def score_display(self, obj):
        pct = obj.score_percentage
        color = '#059669' if pct >= 70 else '#D97706' if pct >= 50 else '#DC2626'
        return format_html(
            '<span style="color:{}; font-weight:700;">{}/{} ({}%)</span>',
            color, obj.correct_count, obj.total_questions, pct
        )
