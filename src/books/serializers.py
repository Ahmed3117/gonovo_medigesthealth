from rest_framework import serializers

from books.models import Book, Specialty, Topic, UserBookAccess
from learning.models import (
    UserTopicProgress, UserBookmark, UserHighlight, UserNote,
)


# ─────────────────────────────────────────────
# Shared / Nested
# ─────────────────────────────────────────────
class TopicMiniSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['id', 'title', 'slug', 'is_completed', 'progress_percentage']

    def _get_progress(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if not user or not user.is_authenticated:
            return None
        key = f'_progress_map_{user.pk}'
        progress_map = self.context.get(key)
        if progress_map is None:
            return UserTopicProgress.objects.filter(
                user=user, topic=obj
            ).first()
        return progress_map.get(str(obj.pk))

    def get_is_completed(self, obj):
        p = self._get_progress(obj)
        return p.is_completed if p else False

    def get_progress_percentage(self, obj):
        p = self._get_progress(obj)
        if not p:
            return 0
        if p.is_completed:
            return 100
        est = obj.estimated_tasks
        if est > 0:
            return round((p.tasks_completed / est) * 100)
        return 0


class SpecialtySerializer(serializers.ModelSerializer):
    topics = TopicMiniSerializer(many=True, read_only=True)
    topic_count = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Specialty
        fields = [
            'id', 'name', 'slug', 'icon', 'progress_percentage',
            'topic_count', 'topics',
        ]

    def get_progress_percentage(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if not user or not user.is_authenticated:
            return 0
        total_topics = obj.topics.count()
        if total_topics == 0:
            return 0
        completed = UserTopicProgress.objects.filter(
            user=user, topic__specialty=obj, is_completed=True
        ).count()
        return round((completed / total_topics) * 100)


# ─────────────────────────────────────────────
# 4.1  My Books
# ─────────────────────────────────────────────
class MyBookSerializer(serializers.ModelSerializer):
    last_topic_title = serializers.SerializerMethodField()
    last_specialty_name = serializers.SerializerMethodField()
    last_accessed = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'slug', 'cover_image', 'last_topic_title',
            'last_specialty_name', 'last_accessed', 'progress_percentage',
        ]

    def _last_progress(self, obj):
        user = self.context['request'].user
        return UserTopicProgress.objects.filter(
            user=user, topic__specialty__book=obj,
        ).order_by('-updated_at').first()

    def get_last_topic_title(self, obj):
        p = self._last_progress(obj)
        return p.topic.title if p else None

    def get_last_specialty_name(self, obj):
        p = self._last_progress(obj)
        return p.topic.specialty.name if p else None

    def get_last_accessed(self, obj):
        p = self._last_progress(obj)
        return p.updated_at if p else None

    def get_progress_percentage(self, obj):
        user = self.context['request'].user
        total_topics = Topic.objects.filter(specialty__book=obj).count()
        if total_topics == 0:
            return 0
        completed = UserTopicProgress.objects.filter(
            user=user, topic__specialty__book=obj, is_completed=True,
        ).count()
        return round((completed / total_topics) * 100)


# ─────────────────────────────────────────────
# 4.2  Store Books
# ─────────────────────────────────────────────
class StoreBookSerializer(serializers.ModelSerializer):
    topic_count = serializers.IntegerField(read_only=True)
    flashcard_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'slug', 'cover_image', 'price',
            'topic_count', 'flashcard_count', 'status',
        ]

    def get_flashcard_count(self, obj):
        from flashcards.models import Flashcard
        return Flashcard.objects.filter(book=obj).count()


# ─────────────────────────────────────────────
# 4.3  Book Detail
# ─────────────────────────────────────────────
class BookDetailSerializer(serializers.ModelSerializer):
    specialties = SpecialtySerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'slug', 'cover_image',
            'progress_percentage', 'specialties',
        ]

    def get_progress_percentage(self, obj):
        user = self.context['request'].user
        total = Topic.objects.filter(specialty__book=obj).count()
        if total == 0:
            return 0
        completed = UserTopicProgress.objects.filter(
            user=user, topic__specialty__book=obj, is_completed=True,
        ).count()
        return round((completed / total) * 100)


# ─────────────────────────────────────────────
# 4.4-4.6  Bookmarks
# ─────────────────────────────────────────────
class BookmarkSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model = UserBookmark
        fields = [
            'id', 'topic', 'topic_title', 'section_anchor',
            'label', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'topic': {'write_only': False},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ─────────────────────────────────────────────
# 4.7-4.8  Notes & Highlights
# ─────────────────────────────────────────────
class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHighlight
        fields = [
            'id', 'topic', 'highlighted_text', 'start_offset',
            'end_offset', 'color', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNote
        fields = [
            'id', 'topic', 'content', 'position_offset',
            'highlight', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ─────────────────────────────────────────────
# 5.1  Topic Content (Reading Interface)
# ─────────────────────────────────────────────
class TopicDetailSerializer(serializers.ModelSerializer):
    specialty = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    test_your_knowledge = serializers.SerializerMethodField()
    pagination = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'slug', 'specialty', 'book',
            'content', 'key_points', 'is_completed', 'is_bookmarked',
            'progress', 'test_your_knowledge', 'pagination',
        ]

    def get_specialty(self, obj):
        return {
            'id': str(obj.specialty.id),
            'name': obj.specialty.name,
            'slug': obj.specialty.slug,
        }

    def get_book(self, obj):
        book = obj.specialty.book
        return {
            'id': str(book.id),
            'title': book.title,
            'slug': book.slug,
        }

    def _user_progress(self, obj):
        if not hasattr(self, '_cached_progress'):
            user = self.context['request'].user
            self._cached_progress = UserTopicProgress.objects.filter(
                user=user, topic=obj,
            ).first()
        return self._cached_progress

    def get_is_completed(self, obj):
        p = self._user_progress(obj)
        return p.is_completed if p else False

    def get_is_bookmarked(self, obj):
        user = self.context['request'].user
        return UserBookmark.objects.filter(user=user, topic=obj).exists()

    def get_progress(self, obj):
        p = self._user_progress(obj)
        return {
            'last_read_section': p.last_read_section if p else '',
            'reading_time_seconds': p.reading_time_seconds if p else 0,
            'tasks_completed': p.tasks_completed if p else 0,
            'estimated_tasks': obj.estimated_tasks,
        }

    def get_test_your_knowledge(self, obj):
        from questions.models import Question, UserQuestionAttempt
        user = self.context['request'].user
        total = Question.objects.filter(topic=obj).count()
        answered = UserQuestionAttempt.objects.filter(
            user=user, question__topic=obj,
        ).values('question').distinct().count()
        return {'total_questions': total, 'answered_questions': answered}

    def get_pagination(self, obj):
        siblings = list(
            Topic.objects.filter(specialty=obj.specialty)
            .order_by('display_order', 'title')
            .values_list('slug', 'title')
        )
        slugs = [s[0] for s in siblings]
        try:
            idx = slugs.index(obj.slug)
        except ValueError:
            idx = 0

        prev_topic = (
            {'slug': siblings[idx - 1][0], 'title': siblings[idx - 1][1]}
            if idx > 0 else None
        )
        next_topic = (
            {'slug': siblings[idx + 1][0], 'title': siblings[idx + 1][1]}
            if idx < len(siblings) - 1 else None
        )
        return {
            'current_position': idx + 1,
            'total_topics': len(siblings),
            'previous_topic': prev_topic,
            'next_topic': next_topic,
        }


# ─────────────────────────────────────────────
# 5.2  Update Topic Progress
# ─────────────────────────────────────────────
class TopicProgressUpdateSerializer(serializers.Serializer):
    is_completed = serializers.BooleanField(required=False)
    last_read_section = serializers.CharField(required=False, allow_blank=True)
    reading_time_seconds = serializers.IntegerField(required=False, min_value=0)
