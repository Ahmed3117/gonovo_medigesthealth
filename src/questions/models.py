import uuid
from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Question(models.Model):
    """
    A multiple-choice question (MCQ) linked to a specialty/topic.
    Mirrors the MKSAP Question Bank format:
    - Question stem with optional image
    - 5 options (A–E) with one correct answer
    - Detailed explanation with educational objective
    """

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.CASCADE, related_name='questions',
        help_text='The specialty this question belongs to.'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='questions',
        help_text='Optional: specific topic this question relates to.'
    )

    # Question content
    question_text = CKEditor5Field(
        config_name='default',
        help_text='The question stem. Can include formatted text, images, and tables.'
    )
    question_image = models.ImageField(
        upload_to='questions/images/', blank=True, null=True,
        help_text='Optional clinical image/figure for the question.'
    )

    # Options (A through E)
    option_a = models.TextField(help_text='Option A text.')
    option_b = models.TextField(help_text='Option B text.')
    option_c = models.TextField(help_text='Option C text.')
    option_d = models.TextField(help_text='Option D text.')
    option_e = models.TextField(blank=True, help_text='Option E text (optional for 4-option questions).')

    CORRECT_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
    ]
    correct_answer = models.CharField(
        max_length=1, choices=CORRECT_CHOICES,
        help_text='Which option is the correct answer.'
    )

    # Explanation & metadata
    explanation = CKEditor5Field(
        config_name='default', blank=True,
        help_text='Detailed explanation shown after answering.'
    )
    educational_objective = models.TextField(
        blank=True,
        help_text='The educational objective tested by this question.'
    )
    difficulty = models.CharField(
        max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['specialty__name', 'created_at']

    def __str__(self):
        text = self.question_text[:80] if self.question_text else 'New Question'
        # Strip HTML tags for display
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        return f'Q: {clean[:80]}...' if len(clean) > 80 else f'Q: {clean}'


class UserQuestionAttempt(models.Model):
    """
    Records each time a user attempts a question.
    Used for analytics, progress tracking, and "Saved Questions" feature.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='question_attempts'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='attempts'
    )
    selected_answer = models.CharField(
        max_length=1, choices=Question.CORRECT_CHOICES
    )
    is_correct = models.BooleanField()
    time_spent_seconds = models.PositiveIntegerField(default=0)
    is_saved = models.BooleanField(
        default=False, help_text='User bookmarked/saved this question.'
    )
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Question Attempt'
        verbose_name_plural = 'Question Attempts'
        ordering = ['-attempted_at']

    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f'{self.user.email} {status} Q:{self.question_id}'


class QuizSession(models.Model):
    """
    A quiz/test session created by a user.
    Groups multiple question attempts into a single quiz run.
    Supports both custom quizzes and exam mode.
    """

    class Mode(models.TextChoices):
        PRACTICE = 'practice', 'Practice'
        EXAM = 'exam', 'Exam Mode'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='quiz_sessions'
    )
    mode = models.CharField(
        max_length=10, choices=Mode.choices, default=Mode.PRACTICE
    )
    specialties = models.ManyToManyField(
        'books.Specialty', blank=True,
        help_text='Specialties included in this quiz.'
    )
    total_questions = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    total_time_seconds = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Quiz Session'
        verbose_name_plural = 'Quiz Sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.email} — {self.mode} ({self.correct_count}/{self.total_questions})'

    @property
    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_count / self.total_questions) * 100, 1)
