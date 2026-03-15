import uuid
from django.db import models

class FAQCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text='E.g., "Reading & Textbooks", "Practice Questions"')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'FAQ Category'
        verbose_name_plural = 'FAQ Categories'
        ordering = ['display_order']

    def __str__(self):
        return self.name

class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField(help_text='The answer to the FAQ.')
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category__display_order', 'display_order']

    def __str__(self):
        return self.question

class ContactMethod(models.Model):
    class IconType(models.TextChoices):
        EMAIL = 'email', 'Email'
        PHONE = 'phone', 'Phone'
        LINK = 'link', 'Link'
        CHAT = 'chat', 'Chat'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text='E.g., "support@medigest.com" or "1-800-MEDIGEST"')
    subtitle = models.CharField(max_length=200, help_text='E.g., "Email Support", "Phone Support"')
    icon_type = models.CharField(max_length=20, choices=IconType.choices, default=IconType.EMAIL)
    action_text = models.CharField(max_length=200, help_text='E.g., "Get help from our support team →"')
    action_url = models.CharField(max_length=500, help_text='E.g., "mailto:support@medigest.com" or "tel:18006334437"')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Contact Method'
        verbose_name_plural = 'Contact Methods'
        ordering = ['display_order']

    def __str__(self):
        return f"{self.subtitle}: {self.title}"
