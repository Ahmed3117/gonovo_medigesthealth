import os

from django.db.models import Count
from django.http import FileResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, Topic, UserBookAccess
from learning.models import (
    UserTopicProgress, UserBookmark, UserHighlight, UserNote,
)
from .serializers import (
    MyBookSerializer,
    StoreBookSerializer,
    BookDetailSerializer,
    BookmarkSerializer,
    HighlightSerializer,
    NoteSerializer,
    TopicDetailSerializer,
    TopicProgressUpdateSerializer,
)


# ─────────────────────────────────────────────
# Helper: Stats summary (reused across pages)
# ─────────────────────────────────────────────
def _build_stats(user):
    """Reusable stats block for Dashboard, Syllabus, Board Basics, etc."""
    from questions.models import UserQuestionAttempt, QuizSession
    from learning.models import UserStudySession
    from django.utils import timezone
    from datetime import timedelta

    # Overall progress: pages read / total pages across owned books
    owned_book_ids = UserBookAccess.objects.filter(
        user=user
    ).values_list('book_id', flat=True)

    owned_books = Book.objects.filter(id__in=owned_book_ids)
    total_pages = sum(b.total_pages for b in owned_books)

    # Pages read = sum of page ranges of completed topics
    completed_progress = UserTopicProgress.objects.filter(
        user=user, topic__specialty__book_id__in=owned_book_ids,
        is_completed=True,
    ).select_related('topic')
    pages_read = sum(
        (p.topic.end_page - p.topic.start_page + 1)
        for p in completed_progress
        if p.topic.end_page and p.topic.start_page
    )

    if total_pages > 0:
        progress_pct = min(round((pages_read / total_pages) * 100), 100)
        detail = f'{pages_read} / {total_pages} pages'
    else:
        # Fallback to topic-based if no page data yet
        total_topics = Topic.objects.filter(
            specialty__book_id__in=owned_book_ids
        ).count()
        completed_topics = completed_progress.count()
        progress_pct = round((completed_topics / total_topics) * 100) if total_topics else 0
        detail = f'{completed_topics} / {total_topics} topics'

    # Quiz average: last 10 quiz sessions
    recent_sessions = QuizSession.objects.filter(
        user=user, is_completed=True,
    ).order_by('-completed_at')[:10]
    if recent_sessions:
        scores = []
        for s in recent_sessions:
            total = s.attempts.count()
            correct = s.attempts.filter(is_correct=True).count()
            if total > 0:
                scores.append(round((correct / total) * 100))
        quiz_avg = round(sum(scores) / len(scores)) if scores else 0
    else:
        quiz_avg = 0

    # Study time this week
    week_start = timezone.now() - timedelta(days=7)
    weekly_seconds = (
        UserStudySession.objects.filter(
            user=user, started_at__gte=week_start,
        ).values_list('duration_seconds', flat=True)
    )
    total_secs = sum(weekly_seconds)
    study_hours = round(total_secs / 3600, 1)

    return {
        'overall_progress': {
            'percentage': progress_pct,
            'detail': detail,
        },
        'bank_average_score': {
            'percentage': quiz_avg,
            'detail': 'Last 10 quizzes',
        },
        'study_time': {
            'hours': study_hours,
            'detail': 'This week',
        },
        'study_streak': {
            'days': user.current_study_streak,
            'detail': 'Keep it up!' if user.current_study_streak > 0 else 'Start studying!',
        },
    }


# ═════════════════════════════════════════════
# 4.1  My Books
# ═════════════════════════════════════════════
class MyBooksView(APIView):
    """GET /api/v1/syllabus/my-books/"""

    def get(self, request):
        owned_ids = UserBookAccess.objects.filter(
            user=request.user
        ).values_list('book_id', flat=True)
        books = Book.objects.filter(id__in=owned_ids)
        serializer = MyBookSerializer(
            books, many=True, context={'request': request}
        )
        return Response({
            'stats': _build_stats(request.user),
            'books': serializer.data,
        })


# ═════════════════════════════════════════════
# 4.2  Store Books
# ═════════════════════════════════════════════
class StoreBooksView(generics.ListAPIView):
    """GET /api/v1/syllabus/store/"""

    serializer_class = StoreBookSerializer

    def get_queryset(self):
        owned_ids = UserBookAccess.objects.filter(
            user=self.request.user
        ).values_list('book_id', flat=True)
        return (
            Book.objects.exclude(id__in=owned_ids)
            .filter(status=Book.Status.ACTIVE)
        )


# ═════════════════════════════════════════════
# 4.3  Book Detail
# ═════════════════════════════════════════════
class BookDetailView(generics.RetrieveAPIView):
    """GET /api/v1/syllabus/books/{book_slug}/"""

    serializer_class = BookDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'book_slug'

    def get_queryset(self):
        return Book.objects.prefetch_related('specialties__topics')


# ═════════════════════════════════════════════
# 4.3b  Secure PDF Serving
# ═════════════════════════════════════════════
class BookPDFView(APIView):
    """
    GET /api/v1/syllabus/books/{book_slug}/pdf/

    Streams the book PDF through an authenticated endpoint.
    The user must own the book (have UserBookAccess) to access the PDF.
    This prevents exposing the raw file URL to the frontend.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, book_slug):
        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            return Response(
                {'detail': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify the user owns this book
        has_access = UserBookAccess.objects.filter(
            user=request.user, book=book,
        ).exists()
        if not has_access:
            return Response(
                {'detail': 'You do not have access to this book.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify a PDF file exists
        if not book.pdf_file:
            return Response(
                {'detail': 'No PDF file available for this book.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Stream the file
        file_path = book.pdf_file.path
        if not os.path.exists(file_path):
            return Response(
                {'detail': 'PDF file not found on server.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf',
        )
        # Inline display (not download), with the book title as filename
        safe_title = book.slug or 'book'
        response['Content-Disposition'] = f'inline; filename="{safe_title}.pdf"'
        # Prevent caching for content protection
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response


# ═════════════════════════════════════════════
# 4.4-4.6  Bookmarks CRUD
# ═════════════════════════════════════════════
class BookmarkListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/syllabus/bookmarks/  — list user bookmarks
    POST /api/v1/syllabus/bookmarks/  — create bookmark
    """

    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return UserBookmark.objects.filter(
            user=self.request.user
        ).select_related('topic')

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response({
            'count': qs.count(),
            'bookmarks': serializer.data,
        })


class BookmarkDeleteView(generics.DestroyAPIView):
    """DELETE /api/v1/syllabus/bookmarks/{pk}/"""

    serializer_class = BookmarkSerializer
    lookup_url_kwarg = 'bookmark_id'

    def get_queryset(self):
        return UserBookmark.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 4.7-4.8  Notes & Highlights (List + Detail)
# ═════════════════════════════════════════════
class NotesHighlightsListView(APIView):
    """GET /api/v1/syllabus/notes-highlights/ — groups by topic"""

    def get(self, request):
        user = request.user
        # Get all topics that have notes or highlights
        highlight_topics = (
            UserHighlight.objects.filter(user=user)
            .values('topic_id', 'topic__title')
            .annotate(highlights_count=Count('id'))
        )
        note_topics = (
            UserNote.objects.filter(user=user)
            .values('topic_id', 'topic__title')
            .annotate(notes_count=Count('id'))
        )

        # Merge
        topic_map = {}
        for h in highlight_topics:
            tid = str(h['topic_id'])
            topic_map.setdefault(tid, {
                'topic_id': tid,
                'topic_title': h['topic__title'],
                'highlights_count': 0,
                'notes_count': 0,
            })
            topic_map[tid]['highlights_count'] = h['highlights_count']

        for n in note_topics:
            tid = str(n['topic_id'])
            topic_map.setdefault(tid, {
                'topic_id': tid,
                'topic_title': n['topic__title'],
                'highlights_count': 0,
                'notes_count': 0,
            })
            topic_map[tid]['notes_count'] = n['notes_count']

        topics = list(topic_map.values())
        total = sum(t['highlights_count'] + t['notes_count'] for t in topics)

        return Response({
            'total_count': total,
            'topics': topics,
        })


class NotesHighlightsDetailView(APIView):
    """GET /api/v1/syllabus/notes-highlights/{topic_id}/"""

    def get(self, request, topic_id):
        user = request.user
        topic = Topic.objects.filter(id=topic_id).first()
        if not topic:
            return Response(
                {'detail': 'Topic not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        highlights = UserHighlight.objects.filter(user=user, topic=topic)
        notes = UserNote.objects.filter(user=user, topic=topic)

        return Response({
            'topic_id': str(topic.id),
            'topic_title': topic.title,
            'highlights': HighlightSerializer(highlights, many=True).data,
            'notes': NoteSerializer(notes, many=True).data,
        })


# ═════════════════════════════════════════════
# 4.9-4.10  Highlight CRUD
# ═════════════════════════════════════════════
class HighlightCreateView(generics.CreateAPIView):
    """POST /api/v1/syllabus/highlights/"""

    serializer_class = HighlightSerializer


class HighlightDeleteView(generics.DestroyAPIView):
    """DELETE /api/v1/syllabus/highlights/{pk}/"""

    serializer_class = HighlightSerializer
    lookup_url_kwarg = 'highlight_id'

    def get_queryset(self):
        return UserHighlight.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 4.11-4.13  Note CRUD
# ═════════════════════════════════════════════
class NoteCreateView(generics.CreateAPIView):
    """POST /api/v1/syllabus/notes/"""

    serializer_class = NoteSerializer


class NoteUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/syllabus/notes/{pk}/"""

    serializer_class = NoteSerializer
    lookup_url_kwarg = 'note_id'
    http_method_names = ['patch']

    def get_queryset(self):
        return UserNote.objects.filter(user=self.request.user)


class NoteDeleteView(generics.DestroyAPIView):
    """DELETE /api/v1/syllabus/notes/{pk}/"""

    serializer_class = NoteSerializer
    lookup_url_kwarg = 'note_id'

    def get_queryset(self):
        return UserNote.objects.filter(user=self.request.user)


# ═════════════════════════════════════════════
# 5.1  Topic Content (Reading)
# ═════════════════════════════════════════════
class TopicDetailView(generics.RetrieveAPIView):
    """GET /api/v1/syllabus/topics/{topic_slug}/"""

    serializer_class = TopicDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'topic_slug'

    def get_queryset(self):
        return Topic.objects.select_related('specialty__book')


# ═════════════════════════════════════════════
# 5.2  Update Topic Progress
# ═════════════════════════════════════════════
class TopicProgressUpdateView(APIView):
    """PATCH /api/v1/syllabus/topics/{topic_slug}/progress/"""

    def patch(self, request, topic_slug):
        topic = Topic.objects.filter(slug=topic_slug).first()
        if not topic:
            return Response(
                {'detail': 'Topic not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TopicProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        progress, _ = UserTopicProgress.objects.get_or_create(
            user=request.user, topic=topic,
        )

        data = serializer.validated_data
        if 'is_completed' in data:
            progress.is_completed = data['is_completed']
        if 'last_read_section' in data:
            progress.last_read_section = data['last_read_section']
        if 'last_page_read' in data:
            progress.last_page_read = data['last_page_read']
        if 'reading_time_seconds' in data:
            progress.reading_time_seconds += data['reading_time_seconds']
        progress.save()

        return Response({
            'is_completed': progress.is_completed,
            'last_read_section': progress.last_read_section,
            'last_page_read': progress.last_page_read,
            'reading_time_seconds': progress.reading_time_seconds,
            'tasks_completed': progress.tasks_completed,
            'estimated_tasks': topic.estimated_tasks,
        })
