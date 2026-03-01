import random

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, UserBookAccess
from questions.models import Question, UserQuestionAttempt, QuizSession
from .serializers import (
    QuestionRowSerializer,
    QuestionDetailSerializer,
    SubmitAnswerSerializer,
    QuizSessionSerializer,
    CreateQuizSerializer,
)


# ═════════════════════════════════════════════
# 6.1  Question Bank Main Page
# ═════════════════════════════════════════════
class QuestionBankMainView(APIView):
    """GET /api/v1/question-bank/"""

    def get(self, request):
        user = request.user

        # Stats
        total_attempts = UserQuestionAttempt.objects.filter(user=user)
        answered_ids = total_attempts.values('question').distinct().count()
        total_q = Question.objects.filter(is_active=True).count()
        pct = round((answered_ids / total_q) * 100) if total_q else 0

        recent_10 = QuizSession.objects.filter(
            user=user, is_completed=True,
        ).order_by('-completed_at')[:10]
        scores = []
        for s in recent_10:
            t = s.attempts.count()
            c = s.attempts.filter(is_correct=True).count()
            if t > 0:
                scores.append(round((c / t) * 100))
        avg_score = round(sum(scores) / len(scores)) if scores else 0

        quiz_completed = QuizSession.objects.filter(
            user=user, is_completed=True
        ).count()
        quiz_started = QuizSession.objects.filter(
            user=user, is_completed=False
        ).count()

        # Question sets by book
        owned_ids = UserBookAccess.objects.filter(
            user=user
        ).values_list('book_id', flat=True)
        books = Book.objects.filter(id__in=owned_ids)
        question_sets = []
        for book in books:
            total = Question.objects.filter(
                specialty__book=book, is_active=True,
            ).count()
            answered = UserQuestionAttempt.objects.filter(
                user=user, question__specialty__book=book,
            ).values('question').distinct().count()
            question_sets.append({
                'id': str(book.id),
                'book_title': book.title,
                'book_slug': book.slug,
                'total_questions': total,
                'progress_percentage': round((answered / total) * 100) if total else 0,
            })

        return Response({
            'stats': {
                'completion': {
                    'percentage': pct,
                    'completed_questions': answered_ids,
                },
                'average_score': {
                    'percentage': avg_score,
                    'detail': 'Last 10 quizzes',
                },
                'custom_quizzes': {
                    'completed': quiz_completed,
                    'started': quiz_started,
                },
            },
            'question_sets': question_sets,
        })


# ═════════════════════════════════════════════
# 6.2  Question Set Detail (by Book)
# ═════════════════════════════════════════════
class QuestionSetDetailView(APIView):
    """GET /api/v1/question-bank/sets/{book_slug}/"""

    def get(self, request, book_slug):
        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            return Response(
                {'detail': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        questions = Question.objects.filter(
            specialty__book=book, is_active=True
        )
        total = questions.count()
        attempts = UserQuestionAttempt.objects.filter(
            user=request.user, question__specialty__book=book,
        )
        answered = attempts.values('question').distinct().count()
        correct = attempts.filter(is_correct=True).values('question').distinct().count()
        incorrect = attempts.filter(is_correct=False).values('question').distinct().count()

        # Recent answers
        recent_ids = (
            attempts.order_by('-attempted_at')
            .values_list('question_id', flat=True)[:10]
        )
        recent_qs = Question.objects.filter(id__in=recent_ids)

        return Response({
            'book_title': book.title,
            'total_questions': total,
            'answered_questions': answered,
            'correct_percentage': round((correct / answered) * 100) if answered else 0,
            'incorrect_percentage': round((incorrect / answered) * 100) if answered else 0,
            'progress_percentage': round((answered / total) * 100) if total else 0,
            'recently_answered': QuestionRowSerializer(
                recent_qs, many=True, context={'request': request}
            ).data,
        })


# ═════════════════════════════════════════════
# 6.3  Answered Questions
# ═════════════════════════════════════════════
class AnsweredQuestionsView(generics.ListAPIView):
    """GET /api/v1/question-bank/answered/"""

    serializer_class = QuestionRowSerializer

    def get_queryset(self):
        user = self.request.user
        answered_ids = UserQuestionAttempt.objects.filter(
            user=user,
        ).values_list('question_id', flat=True).distinct()

        qs = Question.objects.filter(id__in=answered_ids)

        # Optional filters
        specialty = self.request.query_params.get('specialty')
        answer_status = self.request.query_params.get('status')

        if specialty:
            qs = qs.filter(specialty_id=specialty)

        if answer_status == 'correct':
            correct_ids = UserQuestionAttempt.objects.filter(
                user=user, is_correct=True,
            ).values_list('question_id', flat=True)
            qs = qs.filter(id__in=correct_ids)
        elif answer_status == 'incorrect':
            incorrect_ids = UserQuestionAttempt.objects.filter(
                user=user, is_correct=False,
            ).values_list('question_id', flat=True)
            qs = qs.filter(id__in=incorrect_ids)

        return qs


# ═════════════════════════════════════════════
# 6.4  Saved Questions
# ═════════════════════════════════════════════
class SavedQuestionsView(generics.ListAPIView):
    """GET /api/v1/question-bank/saved/"""

    serializer_class = QuestionRowSerializer

    def get_queryset(self):
        user = self.request.user
        saved_ids = UserQuestionAttempt.objects.filter(
            user=user, is_saved=True,
        ).values_list('question_id', flat=True).distinct()

        qs = Question.objects.filter(id__in=saved_ids)

        specialty = self.request.query_params.get('specialty')
        if specialty:
            qs = qs.filter(specialty_id=specialty)

        return qs


# ═════════════════════════════════════════════
# 6.5  Toggle Save Question
# ═════════════════════════════════════════════
class ToggleSaveQuestionView(APIView):
    """POST /api/v1/question-bank/questions/{question_id}/toggle-save/"""

    def post(self, request, question_id):
        attempt = UserQuestionAttempt.objects.filter(
            user=request.user, question_id=question_id,
        ).order_by('-attempted_at').first()

        if attempt:
            attempt.is_saved = not attempt.is_saved
            attempt.save(update_fields=['is_saved'])
            return Response({'is_saved': attempt.is_saved})

        # No attempt yet — create a placeholder
        question = Question.objects.filter(id=question_id).first()
        if not question:
            return Response(
                {'detail': 'Question not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({'is_saved': False})


# ═════════════════════════════════════════════
# 6.6  Custom Quizzes List
# ═════════════════════════════════════════════
class CustomQuizListView(generics.ListAPIView):
    """GET /api/v1/question-bank/custom-quizzes/"""

    serializer_class = QuizSessionSerializer

    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 6.7  Create Custom Quiz
# ═════════════════════════════════════════════
class CreateCustomQuizView(APIView):
    """POST /api/v1/question-bank/custom-quizzes/"""

    def post(self, request):
        serializer = CreateQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        template = d['template']

        # Template presets
        if template == 'lka_practice':
            d['mode'] = QuizSession.Mode.LKA_PRACTICE
            d['time_limit_per_question'] = 300
        elif template == 'exam_practice':
            d['mode'] = QuizSession.Mode.EXAM
            d['time_limit_per_question'] = 90
            d['show_explanations'] = False
            d['number_of_questions'] = 50
        elif template == 'retry_incorrect':
            d['mode'] = QuizSession.Mode.RETRY_INCORRECT
            d['answer_status'] = 'incorrect'

        # Build question pool
        pool = Question.objects.filter(is_active=True)

        if d.get('content_areas'):
            pool = pool.filter(specialty_id__in=d['content_areas'])

        user = request.user
        if d.get('answer_status') == 'incorrect':
            incorrect_ids = UserQuestionAttempt.objects.filter(
                user=user, is_correct=False,
            ).values_list('question_id', flat=True).distinct()
            pool = pool.filter(id__in=incorrect_ids)
        elif d.get('answer_status') == 'correct':
            correct_ids = UserQuestionAttempt.objects.filter(
                user=user, is_correct=True,
            ).values_list('question_id', flat=True).distinct()
            pool = pool.filter(id__in=correct_ids)
        elif d.get('answer_status') == 'unanswered':
            answered_ids = UserQuestionAttempt.objects.filter(
                user=user,
            ).values_list('question_id', flat=True).distinct()
            pool = pool.exclude(id__in=answered_ids)

        if d.get('include_saved'):
            saved_ids = UserQuestionAttempt.objects.filter(
                user=user, is_saved=True,
            ).values_list('question_id', flat=True).distinct()
            pool = pool.filter(id__in=saved_ids)

        # Select questions
        all_ids = list(pool.values_list('id', flat=True))
        num = min(d['number_of_questions'], len(all_ids))
        selected = random.sample(all_ids, num) if all_ids else []

        # Create session
        session = QuizSession.objects.create(
            user=user,
            title=d.get('title', ''),
            mode=d['mode'],
            total_questions=num,
            time_limit_per_question=d.get('time_limit_per_question'),
            show_explanations=d.get('show_explanations', True),
        )

        if d.get('content_areas'):
            session.specialties.set(d['content_areas'])

        first_id = selected[0] if selected else None

        return Response({
            'id': str(session.id),
            'title': session.title,
            'mode': session.mode,
            'total_questions': num,
            'first_question_id': str(first_id) if first_id else None,
        }, status=status.HTTP_201_CREATED)


# ═════════════════════════════════════════════
# 6.8  Delete Custom Quiz
# ═════════════════════════════════════════════
class DeleteCustomQuizView(generics.DestroyAPIView):
    """DELETE /api/v1/question-bank/custom-quizzes/{quiz_id}/"""

    lookup_url_kwarg = 'quiz_id'

    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 6.9  Get Full Question
# ═════════════════════════════════════════════
class QuestionDetailView(generics.RetrieveAPIView):
    """GET /api/v1/question-bank/questions/{question_id}/"""

    serializer_class = QuestionDetailSerializer
    lookup_url_kwarg = 'question_id'

    def get_queryset(self):
        return Question.objects.filter(is_active=True).select_related('specialty')


# ═════════════════════════════════════════════
# 6.10  Submit Answer
# ═════════════════════════════════════════════
class SubmitAnswerView(APIView):
    """POST /api/v1/question-bank/questions/{question_id}/answer/"""

    def post(self, request, question_id):
        question = Question.objects.filter(
            id=question_id, is_active=True,
        ).select_related('specialty', 'topic').first()
        if not question:
            return Response(
                {'detail': 'Question not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        is_correct = d['selected_answer'] == question.correct_answer

        # Create attempt
        attempt = UserQuestionAttempt.objects.create(
            user=request.user,
            question=question,
            selected_answer=d['selected_answer'],
            is_correct=is_correct,
            time_spent_seconds=d['time_spent_seconds'],
            quiz_session_id=d.get('quiz_session_id'),
        )

        # Update quiz session stats if applicable
        session = None
        if d.get('quiz_session_id'):
            try:
                session = QuizSession.objects.get(
                    id=d['quiz_session_id'], user=request.user,
                )
                if is_correct:
                    session.correct_count += 1
                session.total_time_seconds += d['time_spent_seconds']
                session.save(update_fields=['correct_count', 'total_time_seconds'])
            except QuizSession.DoesNotExist:
                pass

        # Peer stats (percentage per option)
        total_attempts = question.attempts.count()
        peer_stats = {}
        for key in ['A', 'B', 'C', 'D', 'E']:
            count = question.attempts.filter(selected_answer=key).count()
            peer_stats[key] = round((count / total_attempts) * 100) if total_attempts else 0

        # Related syllabus content
        related_syllabus = []
        if question.topic:
            related_syllabus.append({
                'topic_id': str(question.topic.id),
                'topic_title': question.topic.title,
                'link': f'/syllabus/topics/{question.topic.slug}/',
            })

        # Build response
        response_data = {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'time_spent_seconds': d['time_spent_seconds'],
            'peer_stats': peer_stats,
            'explanation': question.explanation,
            'key_point': question.key_point,
            'references': question.references or [],
            'related_syllabus': related_syllabus,
            'total_correct': question.attempts.filter(is_correct=True).count(),
            'total_incorrect': question.attempts.filter(is_correct=False).count(),
        }

        return Response(response_data)


# ═════════════════════════════════════════════
# 6.11  Shuffle (Random Practice)
# ═════════════════════════════════════════════
class ShuffleQuestionsView(APIView):
    """POST /api/v1/question-bank/shuffle/"""

    def post(self, request):
        book_id = request.data.get('book_id')
        specialty_id = request.data.get('specialty_id')

        pool = Question.objects.filter(is_active=True)
        if book_id:
            pool = pool.filter(specialty__book_id=book_id)
        if specialty_id:
            pool = pool.filter(specialty_id=specialty_id)

        all_ids = list(pool.values_list('id', flat=True))
        if not all_ids:
            return Response(
                {'detail': 'No questions available.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        num = min(50, len(all_ids))
        selected = random.sample(all_ids, num)

        session = QuizSession.objects.create(
            user=request.user,
            title='Random Practice',
            mode=QuizSession.Mode.PRACTICE,
            total_questions=num,
        )

        return Response({
            'quiz_session_id': str(session.id),
            'first_question_id': str(selected[0]),
        })
