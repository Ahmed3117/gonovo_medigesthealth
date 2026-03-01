import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, UserBookAccess
from webhooks.models import WebhookLog

User = get_user_model()


class PurchaseWebhookView(APIView):
    """
    POST /api/v1/webhooks/purchase/
    Handles e-commerce purchase webhooks.
    Creates user (if needed) and grants book access.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No JWT auth for webhooks

    def post(self, request):
        # 1. Capture raw body FIRST (before request.data consumes the stream)
        raw_body = request._request.body

        # 2. Get client IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')

        # 3. Create webhook log
        log = WebhookLog.objects.create(
            payload_json=request.data,
            ip_address=ip or None,
            processing_status=WebhookLog.ProcessingStatus.RECEIVED,
        )

        # 4. Verify HMAC signature
        secret = getattr(settings, 'WEBHOOK_SIGNING_SECRET', '')
        signature = request.META.get('HTTP_X_WEBHOOK_SIGNATURE', '')
        if secret and signature:
            expected = hmac.new(
                secret.encode(), raw_body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                log.signature_valid = False
                log.processing_status = WebhookLog.ProcessingStatus.INVALID_SIGNATURE
                log.error_message = 'Invalid HMAC signature.'
                log.save()
                return Response(
                    {'detail': 'Invalid signature.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            log.signature_valid = True
        elif secret:
            # Secret is configured but no signature received
            log.signature_valid = False
            log.processing_status = WebhookLog.ProcessingStatus.INVALID_SIGNATURE
            log.error_message = 'No signature header provided.'
            log.save()
            return Response(
                {'detail': 'Missing signature.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 4. Process payload
        log.processing_status = WebhookLog.ProcessingStatus.PROCESSING
        log.save()

        try:
            payload = request.data
            email = payload.get('customer_email', '').strip().lower()
            order_id = str(payload.get('order_id', ''))
            product_ids = payload.get('product_ids', [])

            if not email:
                raise ValueError('Missing customer_email in payload.')
            if not product_ids:
                raise ValueError('Missing product_ids in payload.')

            log.customer_email = email
            log.order_id = order_id

            # 5. Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': payload.get('customer_first_name', ''),
                    'last_name': payload.get('customer_last_name', ''),
                },
            )
            log.user_created = created

            # 6. Grant book access
            books_granted = 0
            for pid in product_ids:
                try:
                    book = Book.objects.get(product_id=str(pid))
                    _, access_created = UserBookAccess.objects.get_or_create(
                        user=user,
                        book=book,
                        defaults={
                            'order_id': order_id,
                            'source': UserBookAccess.Source.WEBHOOK,
                        },
                    )
                    if access_created:
                        books_granted += 1
                except Book.DoesNotExist:
                    pass  # Unknown product_id, skip

            log.books_granted = books_granted
            log.processing_status = WebhookLog.ProcessingStatus.PROCESSED
            log.processed_at = timezone.now()
            log.save()

            return Response({
                'status': 'processed',
                'user_created': created,
                'books_granted': books_granted,
            })

        except Exception as e:
            log.processing_status = WebhookLog.ProcessingStatus.FAILED
            log.error_message = str(e)
            log.processed_at = timezone.now()
            log.save()
            return Response(
                {'detail': f'Processing failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
