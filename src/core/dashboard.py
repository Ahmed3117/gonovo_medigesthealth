"""
Dashboard callback for the Unfold admin index page.
Provides key metrics and statistics for the MEDIGEST Health Platform.
"""
from django.utils import timezone
from datetime import timedelta


def dashboard_callback(request, context):
    """
    Callback to prepare custom variables for the admin dashboard.
    Injected into templates/admin/index.html via UNFOLD settings.
    """
    from accounts.models import User
    from books.models import Book, Specialty, Topic, UserBookAccess
    from questions.models import Question, UserQuestionAttempt, QuizSession
    from flashcards.models import Flashcard
    from certificates.models import CMEActivity, Certificate
    from webhooks.models import WebhookLog

    # Time ranges
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    # User stats
    total_users = User.objects.count()
    new_users_7d = User.objects.filter(created_at__gte=last_7_days).count()
    active_users = User.objects.filter(is_active=True).count()

    # Content stats
    total_books = Book.objects.count()
    active_books = Book.objects.filter(status='active').count()
    total_specialties = Specialty.objects.count()
    total_topics = Topic.objects.count()
    total_questions = Question.objects.filter(is_active=True).count()
    total_flashcards = Flashcard.objects.filter(is_active=True).count()

    # Activity stats
    total_access = UserBookAccess.objects.count()
    recent_access = UserBookAccess.objects.filter(granted_at__gte=last_7_days).count()
    total_attempts = UserQuestionAttempt.objects.count()
    recent_attempts = UserQuestionAttempt.objects.filter(attempted_at__gte=last_7_days).count()
    total_sessions = QuizSession.objects.count()
    total_certificates = Certificate.objects.count()

    # Webhook stats
    total_webhooks = WebhookLog.objects.count()
    failed_webhooks = WebhookLog.objects.filter(processing_status='failed').count()
    recent_webhooks = WebhookLog.objects.filter(received_at__gte=last_7_days).count()

    context.update({
        # User metrics
        "total_users": total_users,
        "new_users_7d": new_users_7d,
        "active_users": active_users,

        # Content metrics
        "total_books": total_books,
        "active_books": active_books,
        "total_specialties": total_specialties,
        "total_topics": total_topics,
        "total_questions": total_questions,
        "total_flashcards": total_flashcards,

        # Activity metrics
        "total_access": total_access,
        "recent_access": recent_access,
        "total_attempts": total_attempts,
        "recent_attempts": recent_attempts,
        "total_sessions": total_sessions,
        "total_certificates": total_certificates,

        # Webhook metrics
        "total_webhooks": total_webhooks,
        "failed_webhooks": failed_webhooks,
        "recent_webhooks": recent_webhooks,
    })

    return context
