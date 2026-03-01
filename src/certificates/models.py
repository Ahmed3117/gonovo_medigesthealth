import uuid
from django.db import models
from django.conf import settings


class CMEActivity(models.Model):
    """
    A CME (Continuing Medical Education) activity that earns credits.
    Admin defines available activities; users complete them to earn credits.
    Figma Part 3: 0.25 credits per question at ≥50% correct.
    """

    class ActivityType(models.TextChoices):
        SYLLABUS = 'syllabus', 'Syllabus Reading'
        QUIZ = 'quiz', 'Quiz Completion'
        BOARD_BASICS = 'board_basics', 'Board Basics'
        QUESTION = 'question', 'Individual Question'

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
    Figma Part 3: Credits grouped by calendar year, 300 max/year.
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
        CMEActivity, on_delete=models.CASCADE, related_name='user_credits',
        null=True, blank=True,
    )

    # ── Figma Part 3: Link to the specific question that earned credit
    question = models.ForeignKey(
        'questions.Question', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cme_credits',
        help_text='The question answered correctly that earned this credit.'
    )

    credits_earned = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.EARNED
    )

    # ── Figma Part 3: Calendar-year tracking ────────────────────────
    credit_year = models.PositiveIntegerField(
        default=2026,
        help_text='Calendar year this credit belongs to (e.g., 2026). Credits cap at 300/year.'
    )

    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User CME Credit'
        verbose_name_plural = 'User CME Credits'
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user.email}: {self.credits_earned} credits — {self.credit_year}'


class CMESubmission(models.Model):
    """
    Records when a user claims/submits CME credits.
    Figma Part 3 (Screen 33): "Claim 0.5 Credits Now!" action.
    Each submission represents a batch of earned credits being formally claimed.
    Supports multiple accreditation bodies (AMA, ABIM, Canadian, Australian, Qatar).
    """

    class AccreditationBody(models.TextChoices):
        AMA = 'ama', 'AMA PRA Category 1 Credits™'
        ABIM_MOC = 'abim_moc', 'ABIM Maintenance of Certification'
        CANADA_RC = 'canada_rc', 'Royal College of Physicians & Surgeons of Canada'
        QATAR_QCHP = 'qatar_qchp', 'Qatar Council for Healthcare Practitioners'
        AUSTRALIA_RACP = 'australia_racp', 'Royal Australasian College of Physicians'

    class SubmissionStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUBMITTED = 'submitted', 'Submitted'
        CONFIRMED = 'confirmed', 'Confirmed'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cme_submissions'
    )
    accreditation_body = models.CharField(
        max_length=20, choices=AccreditationBody.choices, default=AccreditationBody.AMA
    )
    credits_claimed = models.DecimalField(max_digits=5, decimal_places=2)
    credit_year = models.PositiveIntegerField(
        help_text='Calendar year for this submission.'
    )
    status = models.CharField(
        max_length=15, choices=SubmissionStatus.choices, default=SubmissionStatus.PENDING
    )

    # Link to the individual credits being claimed
    credits = models.ManyToManyField(
        UserCMECredit, blank=True, related_name='submissions',
        help_text='The individual earned credits included in this submission.'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'CME Submission'
        verbose_name_plural = 'CME Submissions'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user.email}: {self.credits_claimed} credits → {self.get_accreditation_body_display()}'


class UserCOREProgress(models.Model):
    """
    Tracks a user's CORE (Confirmation of Relevant Education) badge progress.
    Figma Part 3 (Screens 27-28): 11 specialty badges, 3 states.
    Users must score ≥50% on last 30 questions per specialty to earn badge.
    """

    class BadgeStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='core_progress'
    )
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.CASCADE, related_name='core_progress',
        help_text='The CORE specialty this badge tracks.'
    )
    badge_status = models.CharField(
        max_length=15, choices=BadgeStatus.choices, default=BadgeStatus.PENDING
    )
    questions_answered = models.PositiveIntegerField(
        default=0,
        help_text='Total questions answered in this specialty.'
    )
    questions_correct = models.PositiveIntegerField(
        default=0,
        help_text='Total questions answered correctly.'
    )

    # ── 50% threshold tracking (last 30 questions) ──────────────────
    last_30_correct = models.PositiveIntegerField(
        default=0,
        help_text='Correct answers in the last 30 questions (for ≥50% threshold).'
    )
    last_30_total = models.PositiveIntegerField(
        default=0,
        help_text='Total answers in the last 30 questions window.'
    )
    core_quiz_unlocked = models.BooleanField(
        default=False,
        help_text='True when user scores ≥50% on last 30 questions.'
    )

    badge_earned_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Timestamp when the CORE badge was completed.'
    )
    last_accessed_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Last time the user practiced in this specialty.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CORE Progress'
        verbose_name_plural = 'CORE Progress'
        unique_together = ['user', 'specialty']
        ordering = ['specialty__name']

    def __str__(self):
        return f'{self.user.email} — {self.specialty.name}: {self.badge_status}'

    @property
    def progress_percentage(self):
        if self.questions_answered == 0:
            return 0
        total_questions = self.specialty.questions.count()
        if total_questions == 0:
            return 0
        return round((self.questions_answered / total_questions) * 100, 1)

    @property
    def correct_percentage(self):
        if self.questions_answered == 0:
            return 0
        return round((self.questions_correct / self.questions_answered) * 100, 1)


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

    # ── Figma Part 3: Calendar year for CME certificates ────────────
    credit_year = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Calendar year for CME certificates.'
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.user.email} — {self.title}'
