from rest_framework import serializers

from learning.models import UserLearningPlanTopic, UserStudySession


class LearningPlanTopicSerializer(serializers.ModelSerializer):
    """Topics in the user's Learning Plan."""

    topic_title = serializers.CharField(source='topic.title', read_only=True)
    specialty_name = serializers.CharField(
        source='topic.specialty.name', read_only=True
    )
    questions_completed = serializers.SerializerMethodField()
    questions_total = serializers.SerializerMethodField()
    has_started = serializers.SerializerMethodField()

    class Meta:
        model = UserLearningPlanTopic
        fields = [
            'id', 'topic', 'topic_title', 'specialty_name',
            'questions_completed', 'questions_total',
            'has_started', 'added_at',
        ]
        read_only_fields = ['id', 'added_at']

    def get_questions_completed(self, obj):
        from questions.models import UserQuestionAttempt
        user = obj.user
        return UserQuestionAttempt.objects.filter(
            user=user, question__topic=obj.topic,
        ).values('question').distinct().count()

    def get_questions_total(self, obj):
        from questions.models import Question
        return Question.objects.filter(
            topic=obj.topic, is_active=True,
        ).count()

    def get_has_started(self, obj):
        from learning.models import UserTopicProgress
        return UserTopicProgress.objects.filter(
            user=obj.user, topic=obj.topic,
        ).exists()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AvailableTopicSerializer(serializers.Serializer):
    """Topics available to add to Learning Plan."""

    id = serializers.UUIDField(source='pk')
    title = serializers.CharField()
    specialty_name = serializers.SerializerMethodField()
    is_in_plan = serializers.SerializerMethodField()

    def get_specialty_name(self, obj):
        return obj.specialty.name

    def get_is_in_plan(self, obj):
        user = self.context['request'].user
        return UserLearningPlanTopic.objects.filter(
            user=user, topic=obj,
        ).exists()


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStudySession
        fields = [
            'id', 'session_type', 'duration_seconds',
            'book', 'specialty', 'topic',
            'started_at', 'ended_at',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
