import uuid
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
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.ACTIVE
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Order of appearance in the Library. Lower numbers appear first.'
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


class Specialty(models.Model):
    """
    A medical specialty/section within a book.
    Example: Within "Pulmonary" book → "Asthma", "COPD", "Pneumonia", etc.
    Maps to the MKSAP Syllabus specialty structure.
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Specialty'
        verbose_name_plural = 'Specialties'
        ordering = ['display_order', 'name']
        unique_together = ['book', 'slug']

    def __str__(self):
        return f'{self.name} ({self.book.title})'

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
    content = CKEditor5Field(
        config_name='default', blank=True,
        help_text='Rich HTML content — supports headers, images, tables, clinical photos.'
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['display_order', 'title']
        unique_together = ['specialty', 'slug']

    def __str__(self):
        return self.title

    @property
    def book(self):
        return self.specialty.book


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
