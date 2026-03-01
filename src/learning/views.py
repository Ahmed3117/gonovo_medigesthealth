from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, Topic, UserBookAccess
from books.views import _build_stats
from learning.models import (
    RecentActivity, UserTopicProgress, UserLearningPlanTopic,
    UserStudySession,
)
from .serializers import (
    LearningPlanTopicSerializer,
    AvailableTopicSerializer,
    StudySessionSerializer,
)


# ═════════════════════════════════════════════
# 3.1  Dashboard
# ═════════════════════════════════════════════
class DashboardView(APIView):
    """
    GET /api/v1/dashboard/
    Returns stats bar, quick actions (with smart resume), and recent activity.
    """

    def get(self, request):
        user = request.user
        stats = _build_stats(user)

        # ── Smart Resume: Quick Actions ──────────────────
        # 1. Resume reading
        last_reading = UserTopicProgress.objects.filter(
            user=user, is_completed=False,
        ).order_by('-updated_at').first()
        reading_action = {
            'label': 'Continue Reading',
            'type': 'reading',
        }
        if last_reading:
            reading_action['resume'] = {
                'topic_slug': last_reading.topic.slug,
                'topic_title': last_reading.topic.title,
                'section': last_reading.last_read_section,
            }
            reading_action['url'] = f'/syllabus/topics/{last_reading.topic.slug}/'
        else:
            reading_action['url'] = '/syllabus/my-books/'
            reading_action['resume'] = None

        # 2. Resume quiz
        from questions.models import QuizSession
        last_quiz = QuizSession.objects.filter(
            user=user, is_completed=False,
        ).order_by('-started_at').first()
        quiz_action = {
            'label': 'Practice Questions',
            'type': 'quiz',
        }
        if last_quiz:
            quiz_action['resume'] = {
                'quiz_session_id': str(last_quiz.id),
                'quiz_title': last_quiz.title or last_quiz.get_mode_display(),
            }
            quiz_action['url'] = f'/question-bank/custom-quizzes/{last_quiz.id}/'
        else:
            quiz_action['url'] = '/question-bank/'
            quiz_action['resume'] = None

        # 3. Resume flashcards
        from flashcards.models import Flashcard, UserFlashcardProgress
        owned_ids = UserBookAccess.objects.filter(
            user=user,
        ).values_list('book_id', flat=True)
        unreviewed_book = None
        for book_id in owned_ids:
            total = Flashcard.objects.filter(book_id=book_id).count()
            reviewed = UserFlashcardProgress.objects.filter(
                user=user, flashcard__book_id=book_id,
            ).count()
            if total > reviewed:
                unreviewed_book = Book.objects.get(id=book_id)
                break

        flashcard_action = {
            'label': 'Review Flashcards',
            'type': 'flashcard',
        }
        if unreviewed_book:
            flashcard_action['resume'] = {
                'book_slug': unreviewed_book.slug,
                'book_title': unreviewed_book.title,
            }
            flashcard_action['url'] = f'/flashcards/decks/{unreviewed_book.slug}/1/'
        else:
            flashcard_action['url'] = '/flashcards/'
            flashcard_action['resume'] = None

        # ── Today's Goals ────────────────────────────────
        today = timezone.now().date()
        today_reading_secs = UserStudySession.objects.filter(
            user=user, started_at__date=today,
            session_type=UserStudySession.SessionType.READING,
        ).aggregate(t=Sum('duration_seconds'))['t'] or 0

        from questions.models import UserQuestionAttempt
        today_questions = UserQuestionAttempt.objects.filter(
            user=user, attempted_at__date=today,
        ).count()

        goals = {
            'reading': {
                'target_minutes': 30,
                'completed_minutes': round(today_reading_secs / 60),
            },
            'questions': {
                'target': 10,
                'completed': today_questions,
            },
        }

        # ── Recent Activity ──────────────────────────────
        recent = RecentActivity.objects.filter(user=user)[:10]
        recent_data = [
            {
                'id': str(a.id),
                'type': a.activity_type,
                'title': a.title,
                'description': a.description,
                'reference_id': str(a.reference_id) if a.reference_id else None,
                'created_at': a.created_at,
            }
            for a in recent
        ]

        return Response({
            'stats': stats,
            'quick_actions': [reading_action, quiz_action, flashcard_action],
            'todays_goals': goals,
            'recent_activity': recent_data,
        })


# ═════════════════════════════════════════════
# 7.1  Get Learning Plan
# ═════════════════════════════════════════════
class LearningPlanView(APIView):
    """GET /api/v1/learning-plan/"""

    def get(self, request):
        qs = UserLearningPlanTopic.objects.filter(
            user=request.user,
        ).select_related('topic__specialty')

        filter_slug = request.query_params.get('filter')
        if filter_slug:
            qs = qs.filter(topic__specialty__slug=filter_slug)

        serializer = LearningPlanTopicSerializer(
            qs, many=True, context={'request': request}
        )
        return Response({
            'count': qs.count(),
            'topics': serializer.data,
        })


# ═════════════════════════════════════════════
# 7.2  Browse Available Topics
# ═════════════════════════════════════════════
class AvailableTopicsView(generics.ListAPIView):
    """GET /api/v1/learning-plan/available-topics/"""

    serializer_class = AvailableTopicSerializer

    def get_queryset(self):
        qs = Topic.objects.select_related('specialty')
        filter_slug = self.request.query_params.get('filter')
        if filter_slug:
            qs = qs.filter(specialty__slug=filter_slug)
        return qs


# ═════════════════════════════════════════════
# 7.3  Add Topic to Learning Plan
# ═════════════════════════════════════════════
class AddLearningPlanTopicView(generics.CreateAPIView):
    """POST /api/v1/learning-plan/topics/"""

    serializer_class = LearningPlanTopicSerializer


# ═════════════════════════════════════════════
# 7.4  Remove Topic from Learning Plan
# ═════════════════════════════════════════════
class RemoveLearningPlanTopicView(generics.DestroyAPIView):
    """DELETE /api/v1/learning-plan/topics/{entry_id}/"""

    lookup_url_kwarg = 'entry_id'

    def get_queryset(self):
        return UserLearningPlanTopic.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 12.4  Record Study Session
# ═════════════════════════════════════════════
class RecordStudySessionView(generics.CreateAPIView):
    """POST /api/v1/users/me/study-sessions/"""

    serializer_class = StudySessionSerializer

