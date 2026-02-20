import uuid
from django.db import models
from django.conf import settings


class CMEActivity(models.Model):
    """
    A CME (Continuing Medical Education) activity that earns credits.
    Admin defines available activities; users complete them to earn credits.
    """

    class ActivityType(models.TextChoices):
        SYLLABUS = 'syllabus', 'Syllabus Reading'
        QUIZ = 'quiz', 'Quiz Completion'
        BOARD_BASICS = 'board_basics', 'Board Basics'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_type = models.CharField(
        max_length=20, choices=ActivityType.choices
    )
    credits = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text='Number of CME credits earned for completing this activity.'
    )
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cme_activities'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'CME Activity'
        verbose_name_plural = 'CME Activities'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} ({self.credits} credits)'


class UserCMECredit(models.Model):
    """
    Records CME credits earned by a user.
    Tracks when the credit was earned and its status.
    """

    class Status(models.TextChoices):
        EARNED = 'earned', 'Earned'
        SUBMITTED = 'submitted', 'Submitted'
        VERIFIED = 'verified', 'Verified'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cme_credits'
    )
    activity = models.ForeignKey(
        CMEActivity, on_delete=models.CASCADE, related_name='user_credits'
    )
    credits_earned = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.EARNED
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User CME Credit'
        verbose_name_plural = 'User CME Credits'
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user.email}: {self.credits_earned} credits — {self.activity.title}'


class Certificate(models.Model):
    """
    A generated certificate (PDF) for a user.
    Can be for CORE completion, CME credits, or exam results.
    """

    class CertificateType(models.TextChoices):
        CORE = 'core', 'CORE Completion'
        CME = 'cme', 'CME Credits'
        EXAM = 'exam', 'Exam Completion'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_type = models.CharField(
        max_length=10, choices=CertificateType.choices
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(
        upload_to='certificates/pdfs/', blank=True, null=True
    )
    total_credits = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.user.email} — {self.title}'
