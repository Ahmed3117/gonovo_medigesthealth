from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Question, UserQuestionAttempt, QuizSession


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    """
    Admin for managing MCQ questions.
    Uses Unfold's label and header decorators for a premium look.
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

    @display(description='Question', ordering='question_text')
    def question_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.question_text or '')
        return clean[:100] + '...' if len(clean) > 100 else clean

    @display(description='Specialty', ordering='specialty__name')
    def specialty_name(self, obj):
        return obj.specialty.name

    @display(description='Topic')
    def topic_name(self, obj):
        return obj.topic.title if obj.topic else '—'

    @display(
        description='Answer',
        label=True,
    )
    def correct_answer_badge(self, obj):
        return obj.correct_answer

    @display(
        description='Difficulty',
        label={
            'easy': 'success',
            'medium': 'warning',
            'hard': 'danger',
        },
    )
    def difficulty_badge(self, obj):
        return obj.difficulty, obj.get_difficulty_display()


@admin.register(UserQuestionAttempt)
class UserQuestionAttemptAdmin(ModelAdmin):
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

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(description='Question')
    def question_preview(self, obj):
        import re
        clean = re.sub(r'<[^>]+>', '', obj.question.question_text or '')
        return clean[:60] + '...' if len(clean) > 60 else clean

    @display(
        description='Result',
        label={
            True: 'success',
            False: 'danger',
        },
    )
    def result_badge(self, obj):
        if obj.is_correct:
            return True, "✓ Correct"
        return False, "✗ Wrong"


@admin.register(QuizSession)
class QuizSessionAdmin(ModelAdmin):
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

    @display(description='User')
    def user_email(self, obj):
        return obj.user.email

    @display(
        description='Mode',
        label={
            'exam': 'danger',
            'practice': 'info',
        },
    )
    def mode_badge(self, obj):
        return obj.mode, obj.get_mode_display()

    @display(description='Score')
    def score_display(self, obj):
        pct = obj.score_percentage
        return f"{obj.correct_count}/{obj.total_questions} ({pct}%)"
