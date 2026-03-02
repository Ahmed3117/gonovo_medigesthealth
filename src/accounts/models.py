import random
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager — email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for MEDIGEST Health.
    Uses email as the unique identifier instead of username.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        ADMIN = 'admin', 'Admin'
        DOCTOR = 'doctor', 'Doctor'

    class ThemePreference(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'
        SYSTEM = 'system', 'System'

    class FontSize(models.TextChoices):
        SMALL = 'small', 'Small'
        MEDIUM = 'medium', 'Medium'
        LARGE = 'large', 'Large'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Preferences
    theme = models.CharField(
        max_length=10,
        choices=ThemePreference.choices,
        default=ThemePreference.LIGHT,
    )
    font_size = models.CharField(
        max_length=10,
        choices=FontSize.choices,
        default=FontSize.MEDIUM,
    )
    email_notifications = models.BooleanField(default=True)

    # ── Gamification: Study Streak ──────────────────────────────────
    # Figma Part 3 (Board Basics & Flashcards) shows "7 days" study streak.
    # Streak increments each consecutive day the user studies.
    current_study_streak = models.PositiveIntegerField(
        default=0,
        help_text='Current consecutive days of study activity.'
    )
    longest_study_streak = models.PositiveIntegerField(
        default=0,
        help_text='All-time longest study streak (for achievements/display).'
    )
    last_study_date = models.DateField(
        null=True, blank=True,
        help_text='Date of last study activity. Used to calculate streak continuity.'
    )

    # Django auth fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        full = self.get_full_name()
        return full if full.strip() else self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    @property
    def purchased_books_count(self):
        return self.book_access.count()


class PasswordResetOTP(models.Model):
    """
    Stores a 6-digit OTP for password reset.
    Each OTP expires after 10 minutes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='password_reset_otps'
    )
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.user.email} — {"used" if self.is_used else "active"}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    @classmethod
    def generate_for_user(cls, user):
        """Invalidate old OTPs and create a new 6-digit OTP."""
        # Invalidate any existing unused OTPs
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        otp_code = f'{random.randint(0, 999999):06d}'
        otp = cls.objects.create(
            user=user,
            otp=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        return otp
