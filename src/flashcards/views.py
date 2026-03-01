from django.db.models import Max
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, UserBookAccess
from books.views import _build_stats
from flashcards.models import Flashcard, UserFlashcardProgress
from .serializers import FlashcardDetailSerializer, ReviewFlashcardSerializer


# ═════════════════════════════════════════════
# 10.1  Flashcard Decks (Main Page)
# ═════════════════════════════════════════════
class FlashcardDecksView(APIView):
    """GET /api/v1/flashcards/"""

    def get(self, request):
        user = request.user
        owned_ids = UserBookAccess.objects.filter(
            user=user,
        ).values_list('book_id', flat=True)
        books = Book.objects.filter(id__in=owned_ids)

        decks = []
        total_reviewed = 0
        total_flashcards = 0

        for book in books:
            book_cards = Flashcard.objects.filter(book=book)
            count = book_cards.count()
            reviewed = UserFlashcardProgress.objects.filter(
                user=user, flashcard__book=book,
            ).count()
            last = UserFlashcardProgress.objects.filter(
                user=user, flashcard__book=book,
            ).aggregate(last=Max('last_reviewed_at'))['last']

            total_reviewed += reviewed
            total_flashcards += count

            decks.append({
                'id': str(book.id),
                'book_title': book.title,
                'book_slug': book.slug,
                'total_flashcards': count,
                'reviewed_flashcards': reviewed,
                'progress_percentage': round((reviewed / count) * 100) if count else 0,
                'last_accessed': last,
            })

        stats = _build_stats(user)
        # Override overall_progress for flashcards context
        stats['overall_progress'] = {
            'percentage': round((total_reviewed / total_flashcards) * 100) if total_flashcards else 0,
            'detail': f'{total_reviewed} / {total_flashcards} flashcards',
        }

        return Response({
            'stats': stats,
            'decks': decks,
        })


# ═════════════════════════════════════════════
# 10.2  Get Flashcard by Position
# ═════════════════════════════════════════════
class FlashcardByPositionView(APIView):
    """GET /api/v1/flashcards/decks/{book_slug}/{position}/"""

    def get(self, request, book_slug, position):
        book = Book.objects.filter(slug=book_slug).first()
        if not book:
            return Response(
                {'detail': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        cards = Flashcard.objects.filter(
            book=book,
        ).order_by('display_order', 'id').select_related('related_topic')

        total = cards.count()
        if position < 1 or position > total:
            return Response(
                {'detail': f'Position must be between 1 and {total}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = cards[position - 1]  # 0-indexed
        serializer = FlashcardDetailSerializer(
            card, context={'request': request}
        )

        data = serializer.data
        data['position'] = position
        data['navigation'] = {
            'previous_position': position - 1 if position > 1 else None,
            'next_position': position + 1 if position < total else None,
            'has_previous': position > 1,
            'has_next': position < total,
        }

        return Response(data)


# ═════════════════════════════════════════════
# 10.3  Mark Flashcard as Reviewed
# ═════════════════════════════════════════════
class ReviewFlashcardView(APIView):
    """POST /api/v1/flashcards/{flashcard_id}/review/"""

    def post(self, request, flashcard_id):
        flashcard = Flashcard.objects.filter(id=flashcard_id).first()
        if not flashcard:
            return Response(
                {'detail': 'Flashcard not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewFlashcardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        progress, created = UserFlashcardProgress.objects.get_or_create(
            user=request.user,
            flashcard=flashcard,
            defaults={
                'confidence': serializer.validated_data['confidence'],
                'times_reviewed': 1,
                'last_reviewed_at': timezone.now(),
            },
        )

        if not created:
            progress.confidence = serializer.validated_data['confidence']
            progress.times_reviewed += 1
            progress.last_reviewed_at = timezone.now()
            progress.save()

        return Response({
            'flashcard_id': str(flashcard.id),
            'confidence': progress.confidence,
            'times_reviewed': progress.times_reviewed,
            'last_reviewed_at': progress.last_reviewed_at,
        })
