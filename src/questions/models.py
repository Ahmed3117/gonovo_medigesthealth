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
    - Key point, references, and tagging (Figma Part 2)
    """

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    # ── Figma Part 2: Question tagging system ───────────────────────
    class CareType(models.TextChoices):
        AMBULATORY = 'ambulatory', 'Ambulatory'
        INPATIENT = 'inpatient', 'Inpatient'
        EMERGENCY = 'emergency', 'Emergency'
        ICU = 'icu', 'ICU / Critical Care'

    class PatientDemographic(models.TextChoices):
        ADULT = 'adult', 'Adult'
        ELDERLY = 'elderly', 'Age ≥65 y'
        YOUNG_ADULT = 'young_adult', 'Age 18-40 y'
        PREGNANT = 'pregnant', 'Pregnant'
        PEDIATRIC = 'pediatric', 'Pediatric'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Figma: Question Bank groups questions by book ────────────────
    book = models.ForeignKey(
        'books.Book', on_delete=models.CASCADE, related_name='questions',
        null=True, blank=True,
        help_text='The book this question belongs to (for Question Bank grouping).'
    )
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.CASCADE, related_name='questions',
        help_text='The specialty this question belongs to.'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='questions',
        help_text='Optional: specific topic this question relates to.'
    )

    # ── Figma Part 2: \"Related Syllabus Content →\" cross-link ───────
    related_topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='related_questions',
        help_text='Topic linked via \"Related Syllabus Content →\" in the critique section.'
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

    # ── Figma Part 2: Key Point section (separate from explanation) ─
    key_point = models.TextField(
        blank=True,
        help_text='Standalone key takeaway shown in a separate "Key Point" card.'
    )

    # ── Figma Part 2: References with PMID links ───────────────────
    references = models.JSONField(
        default=list, blank=True,
        help_text='List of reference objects. Example: [{"text": "Author et al.", "pmid": "12345678"}]'
    )

    # ── Figma Part 2: Lab values table ──────────────────────────────
    lab_values = models.JSONField(
        default=list, blank=True,
        help_text='Lab values with abnormal flags. Example: [{"name": "Hemoglobin", "value": "8.2", "unit": "g/dL", "flag": "L", "ref_range": "12-16"}]'
    )

    # ── Figma Part 2: Question tags (care type, demographics) ──────
    care_type = models.CharField(
        max_length=20, choices=CareType.choices, blank=True,
        help_text='Care setting tag (e.g., "Ambulatory", "Inpatient").'
    )
    patient_demographic = models.CharField(
        max_length=20, choices=PatientDemographic.choices, blank=True,
        help_text='Patient demographic tag (e.g., "Age ≥65 y").'
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

    # ── Figma Part 2: Link attempt to a quiz session ────────────────
    quiz_session = models.ForeignKey(
        'QuizSession', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='attempts',
        help_text='The quiz session this attempt belongs to (if any).'
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
    Supports practice, exam, LKA, and retry-incorrect modes (Figma Part 2).
    """

    # ── Figma Part 2: 4 quiz templates, not just 2 ─────────────────
    class Mode(models.TextChoices):
        PRACTICE = 'practice', 'Practice'
        EXAM = 'exam', 'Exam Mode'
        LKA_PRACTICE = 'lka', 'LKA Practice'
        RETRY_INCORRECT = 'retry', 'Retry Incorrect'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='quiz_sessions'
    )

    # ── Figma Part 2: Custom quizzes have user-given names ──────────
    title = models.CharField(
        max_length=255, blank=True,
        help_text='User-given name for custom quizzes (e.g., "Cardio Review").'
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

    # ── Figma Part 2: Timing options (untimed, 60s/q, 90s/q) ───────
    time_limit_per_question = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Seconds per question (null = untimed). Figma options: 60s, 90s.'
    )

    # ── Figma Part 2: Show/hide explanations toggle ─────────────────
    show_explanations = models.BooleanField(
        default=True,
        help_text='If False, answer & critique are hidden (exam simulation mode).'
    )

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Quiz Session'
        verbose_name_plural = 'Quiz Sessions'
        ordering = ['-started_at']

    def __str__(self):
        name = self.title or self.mode
        return f'{self.user.email} — {name} ({self.correct_count}/{self.total_questions})'

    @property
    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.correct_count / self.total_questions) * 100, 1)
