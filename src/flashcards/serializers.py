from rest_framework import serializers

from flashcards.models import Flashcard, UserFlashcardProgress


class FlashcardDeckSerializer(serializers.Serializer):
    """Deck info for the flashcards main page."""
    id = serializers.UUIDField()
    book_title = serializers.CharField()
    book_slug = serializers.CharField()
    total_flashcards = serializers.IntegerField()
    reviewed_flashcards = serializers.IntegerField()
    progress_percentage = serializers.IntegerField()
    last_accessed = serializers.DateTimeField(allow_null=True)


class FlashcardDetailSerializer(serializers.ModelSerializer):
    """Single flashcard for the review interface."""
    related_topic = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()
    total_in_deck = serializers.SerializerMethodField()

    class Meta:
        model = Flashcard
        fields = [
            'id', 'display_order', 'front_text', 'back_text',
            'related_topic', 'is_reviewed', 'total_in_deck',
        ]

    def get_related_topic(self, obj):
        if not obj.related_topic:
            return None
        return {
            'id': str(obj.related_topic.id),
            'title': obj.related_topic.title,
            'slug': obj.related_topic.slug,
            'link': f'/syllabus/topics/{obj.related_topic.slug}/',
        }

    def get_is_reviewed(self, obj):
        user = self.context['request'].user
        return UserFlashcardProgress.objects.filter(
            user=user, flashcard=obj,
        ).exists()

    def get_total_in_deck(self, obj):
        if not obj.book:
            return 0
        return Flashcard.objects.filter(book=obj.book).count()


class ReviewFlashcardSerializer(serializers.Serializer):
    confidence = serializers.IntegerField(min_value=0, max_value=4, default=1)
