import uuid
from django.db import models


class WebhookLog(models.Model):
    """
    Logs all incoming webhook requests for debugging and audit.
    Records the raw payload, signature validation status, and processing result.
    """

    class ProcessingStatus(models.TextChoices):
        RECEIVED = 'received', 'Received'
        PROCESSING = 'processing', 'Processing'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'
        INVALID_SIGNATURE = 'invalid_sig', 'Invalid Signature'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(
        max_length=100, blank=True, db_index=True,
        help_text='Order ID extracted from the webhook payload.'
    )
    customer_email = models.EmailField(
        blank=True, help_text='Customer email from the payload.'
    )
    payload_json = models.JSONField(
        default=dict,
        help_text='The complete raw JSON payload received.'
    )
    signature_valid = models.BooleanField(
        default=False,
        help_text='Whether the HMAC signature was valid.'
    )
    processing_status = models.CharField(
        max_length=15,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.RECEIVED,
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error details if processing failed.'
    )
    ip_address = models.GenericIPAddressField(
        blank=True, null=True,
        help_text='IP address of the webhook sender.'
    )
    user_created = models.BooleanField(
        default=False,
        help_text='Whether a new user was created as a result.'
    )
    books_granted = models.PositiveIntegerField(
        default=0,
        help_text='Number of books access was granted for.'
    )

    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Webhook Log'
        verbose_name_plural = 'Webhook Logs'
        ordering = ['-received_at']

    def __str__(self):
        return f'Webhook {self.order_id or "unknown"} — {self.processing_status}'
