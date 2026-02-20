import uuid
from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Flashcard(models.Model):
    """
    A flashcard with front (question/prompt) and back (answer).
    Linked to a specialty and optionally to a specific topic.
    Admin creates these via Django Admin.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.CASCADE, related_name='flashcards',
        help_text='The specialty this flashcard belongs to.'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='flashcards',
        help_text='Optional: specific topic this flashcard relates to.'
    )

    front_text = CKEditor5Field(
        config_name='minimal',
        help_text='The question/prompt side of the flashcard.'
    )
    back_text = CKEditor5Field(
        config_name='minimal',
        help_text='The answer/explanation side of the flashcard.'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['specialty__name', 'created_at']

    def __str__(self):
        import re
        clean = re.sub(r'<[^>]+>', '', self.front_text or '')
        return clean[:80] + '...' if len(clean) > 80 else clean


class UserFlashcardProgress(models.Model):
    """
    Tracks a user's progress on each flashcard.
    Implements spaced repetition with confidence ratings.
    """

    class Confidence(models.IntegerChoices):
        NOT_REVIEWED = 0, 'Not Reviewed'
        NOT_CONFIDENT = 1, 'Not Confident'
        SOMEWHAT = 2, 'Somewhat Confident'
        CONFIDENT = 3, 'Confident'
        VERY_CONFIDENT = 4, 'Very Confident'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='flashcard_progress'
    )
    flashcard = models.ForeignKey(
        Flashcard, on_delete=models.CASCADE, related_name='user_progress'
    )
    confidence = models.IntegerField(
        choices=Confidence.choices, default=Confidence.NOT_REVIEWED
    )
    times_reviewed = models.PositiveIntegerField(default=0)
    next_review_at = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Flashcard Progress'
        verbose_name_plural = 'Flashcard Progress'
        unique_together = ['user', 'flashcard']
        ordering = ['next_review_at']

    def __str__(self):
        return f'{self.user.email} — {self.get_confidence_display()}'


class UserCustomFlashcard(models.Model):
    """
    Custom flashcard created by a user (e.g., from the Syllabus reader).
    Users can create their own flashcards while reading topics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='custom_flashcards'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='custom_flashcards',
        help_text='Topic this flashcard was created from.'
    )
    front_text = models.TextField(help_text='The question/prompt side.')
    back_text = models.TextField(help_text='The answer/explanation side.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Custom Flashcard'
        verbose_name_plural = 'User Custom Flashcards'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email}: {self.front_text[:60]}'
