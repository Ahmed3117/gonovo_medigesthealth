import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Book(models.Model):
    """
    Represents a medical book/product.
    Each book maps to one e-commerce store product via product_id.
    Example: "Pulmonary and Critical Care Medicine" ($60)
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMING_SOON = 'coming_soon', 'Coming Soon'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.CharField(
        max_length=100, unique=True, db_index=True,
        help_text='Maps to the e-commerce store product ID (received from webhook).'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = CKEditor5Field(
        config_name='default', blank=True,
        help_text='Rich description of the book shown in the Library/Store.'
    )
    cover_image = models.ImageField(
        upload_to='books/covers/', blank=True, null=True,
        help_text='Book cover image (3D render preferred).'
    )

    # ── PDF-based content delivery ──────────────────────────────────
    pdf_file = models.FileField(
        upload_to='books/pdfs/', blank=True, null=True,
        help_text='The full book PDF file. Specialties and topics are mapped to page ranges within this PDF.'
    )
    total_pages = models.PositiveIntegerField(
        default=0,
        help_text='Total number of pages in the PDF (auto-set or manually entered).'
    )

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.ACTIVE
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Order of appearance in the Library. Lower numbers appear first.'
    )

    # ── Figma Part 3: Board Basics stats show "450 / 870 pages" ─────
    estimated_pages = models.PositiveIntegerField(
        default=0,
        help_text='Total page count for progress display (e.g., "450 / 870 pages").'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['display_order', 'title']

    def __str__(self):
        return self.title

    @property
    def specialty_count(self):
        return self.specialties.count()

    @property
    def topic_count(self):
        return Topic.objects.filter(specialty__book=self).count()

    @property
    def has_pdf(self):
        return bool(self.pdf_file)


class Specialty(models.Model):
    """
    A medical specialty/section within a book.
    Example: Within "Pulmonary" book → "Asthma", "COPD", "Pneumonia", etc.
    Maps to the MKSAP Syllabus specialty structure.
    Also used as the basis for CORE badges (11 specialties).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='specialties'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    icon = models.ImageField(
        upload_to='books/specialty_icons/', blank=True, null=True,
        help_text='Icon/image for this specialty.'
    )
    description = models.TextField(blank=True, help_text='Brief description of this specialty.')
    display_order = models.PositiveIntegerField(default=0)

    # ── PDF page range mapping ──────────────────────────────────────
    start_page = models.PositiveIntegerField(
        default=0,
        help_text='Starting page number in the book PDF for this specialty (1-indexed).'
    )
    end_page = models.PositiveIntegerField(
        default=0,
        help_text='Ending page number in the book PDF for this specialty (inclusive).'
    )

    # ── Figma Part 3: CORE module has 11 specialty badges ───────────
    is_core_specialty = models.BooleanField(
        default=False,
        help_text='If True, this specialty appears in the CORE certification module with badge tracking.'
    )
    core_display_order = models.PositiveIntegerField(
        default=0,
        help_text='Order of appearance in the CORE badge list (1-11).'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Specialty'
        verbose_name_plural = 'Specialties'
        ordering = ['display_order', 'name']
        unique_together = ['book', 'slug']

    def __str__(self):
        return f'{self.name} ({self.book.title})'

    def clean(self):
        super().clean()
        if self.start_page and self.end_page:
            if self.start_page > self.end_page:
                raise ValidationError({
                    'end_page': 'End page must be greater than or equal to start page.'
                })
            if self.book.total_pages and self.end_page > self.book.total_pages:
                raise ValidationError({
                    'end_page': f'End page ({self.end_page}) exceeds the book total pages ({self.book.total_pages}).'
                })

    @property
    def page_count(self):
        if self.start_page and self.end_page:
            return self.end_page - self.start_page + 1
        return 0

    @property
    def topic_count(self):
        return self.topics.count()


class Topic(models.Model):
    """
    A topic/chapter within a specialty.
    Contains the actual medical content that users read.
    Admin adds content via Django Admin using CKEditor rich text editor.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name='topics'
    )
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500)

    # ── PDF page range mapping ──────────────────────────────────────
    start_page = models.PositiveIntegerField(
        default=0,
        help_text='Starting page number in the book PDF for this topic (1-indexed).'
    )
    end_page = models.PositiveIntegerField(
        default=0,
        help_text='Ending page number in the book PDF for this topic (inclusive).'
    )

    key_points = models.JSONField(
        default=list, blank=True,
        help_text='List of key point strings. Example: ["Point 1", "Point 2"]'
    )
    display_order = models.PositiveIntegerField(default=0)
    is_board_basics = models.BooleanField(
        default=False,
        help_text='If checked, this topic also appears in the Board Basics section.'
    )

    # ── Figma Part 3: Learning Plan shows "0/3 tasks completed" ─────
    # Tasks are sub-items within a topic (reading, quiz, flashcard review, etc.)
    estimated_tasks = models.PositiveIntegerField(
        default=0,
        help_text='Number of tasks associated with this topic (for Learning Plan progress display).'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['display_order', 'title']
        unique_together = ['specialty', 'slug']

    def clean(self):
        super().clean()
        if self.start_page and self.end_page:
            if self.start_page > self.end_page:
                raise ValidationError({
                    'end_page': 'End page must be greater than or equal to start page.'
                })
            # Validate topic pages fall within specialty range
            if self.specialty_id:
                spec = self.specialty
                if spec.start_page and spec.end_page:
                    if self.start_page < spec.start_page or self.end_page > spec.end_page:
                        raise ValidationError({
                            'start_page': (
                                f'Topic page range ({self.start_page}-{self.end_page}) must fall '
                                f'within specialty range ({spec.start_page}-{spec.end_page}).'
                            )
                        })

    def __str__(self):
        return self.title

    @property
    def book(self):
        return self.specialty.book

    @property
    def page_count(self):
        if self.start_page and self.end_page:
            return self.end_page - self.start_page + 1
        return 0


class UserBookAccess(models.Model):
    """
    Tracks which books a user has purchased/been granted access to.
    Created via webhook on purchase or manually by admin.
    """

    class Source(models.TextChoices):
        WEBHOOK = 'webhook', 'Webhook (Auto)'
        MANUAL = 'manual_admin', 'Manual (Admin)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='book_access'
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='user_access'
    )
    order_id = models.CharField(
        max_length=100, blank=True,
        help_text='Order ID from the webhook payload.'
    )
    source = models.CharField(
        max_length=15, choices=Source.choices, default=Source.WEBHOOK
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Book Access'
        verbose_name_plural = 'User Book Access'
        unique_together = ['user', 'book']
        ordering = ['-granted_at']

    def __str__(self):
        return f'{self.user.email} → {self.book.title}'
