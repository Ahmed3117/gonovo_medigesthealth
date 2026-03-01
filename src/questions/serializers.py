from rest_framework import serializers

from questions.models import Question, UserQuestionAttempt, QuizSession


# ─────────────────────────────────────────────
# Question row (list view)
# ─────────────────────────────────────────────
class QuestionRowSerializer(serializers.ModelSerializer):
    """Compact question for lists (Answered, Saved, etc.)"""
    is_correct = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'educational_objective', 'is_correct', 'is_saved', 'tags',
        ]

    def _attempt(self, obj):
        user = self.context['request'].user
        return UserQuestionAttempt.objects.filter(
            user=user, question=obj,
        ).order_by('-attempted_at').first()

    def get_is_correct(self, obj):
        a = self._attempt(obj)
        return a.is_correct if a else None

    def get_is_saved(self, obj):
        a = self._attempt(obj)
        return a.is_saved if a else False

    def get_tags(self, obj):
        return {
            'specialty': obj.specialty.name if obj.specialty else None,
            'care_type': obj.get_care_type_display() if obj.care_type else None,
            'patient_demographic': obj.get_patient_demographic_display() if obj.patient_demographic else None,
        }


# ─────────────────────────────────────────────
# Full question (question-taking interface)
# ─────────────────────────────────────────────
class QuestionDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    user_attempt = serializers.SerializerMethodField()
    total_correct = serializers.SerializerMethodField()
    total_incorrect = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'educational_objective', 'tags',
            'question_text', 'question_image', 'lab_values',
            'options', 'is_saved',
            'user_attempt', 'total_correct', 'total_incorrect',
            'updated_at',
        ]

    def get_tags(self, obj):
        return {
            'specialty': obj.specialty.name if obj.specialty else None,
            'care_type': obj.get_care_type_display() if obj.care_type else None,
            'patient_demographic': obj.get_patient_demographic_display() if obj.patient_demographic else None,
        }

    def get_options(self, obj):
        opts = []
        for key in ['A', 'B', 'C', 'D', 'E']:
            text = getattr(obj, f'option_{key.lower()}', '')
            if text:
                opts.append({'key': key, 'text': text})
        return opts

    def get_is_saved(self, obj):
        user = self.context['request'].user
        return UserQuestionAttempt.objects.filter(
            user=user, question=obj, is_saved=True,
        ).exists()

    def get_user_attempt(self, obj):
        user = self.context['request'].user
        attempt = UserQuestionAttempt.objects.filter(
            user=user, question=obj,
        ).order_by('-attempted_at').first()
        if not attempt:
            return None
        return {
            'selected_answer': attempt.selected_answer,
            'is_correct': attempt.is_correct,
            'time_spent_seconds': attempt.time_spent_seconds,
            'attempted_at': attempt.attempted_at,
        }

    def get_total_correct(self, obj):
        return obj.attempts.filter(is_correct=True).count()

    def get_total_incorrect(self, obj):
        return obj.attempts.filter(is_correct=False).count()


# ─────────────────────────────────────────────
# Answer submission
# ─────────────────────────────────────────────
class SubmitAnswerSerializer(serializers.Serializer):
    selected_answer = serializers.ChoiceField(choices=['A', 'B', 'C', 'D', 'E'])
    time_spent_seconds = serializers.IntegerField(min_value=0, default=0)
    quiz_session_id = serializers.UUIDField(required=False, allow_null=True)


# ─────────────────────────────────────────────
# Quiz session
# ─────────────────────────────────────────────
class QuizSessionSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    last_accessed = serializers.DateTimeField(source='started_at', read_only=True)

    class Meta:
        model = QuizSession
        fields = [
            'id', 'title', 'mode', 'total_questions',
            'correct_count', 'progress_percentage',
            'last_accessed', 'is_completed',
        ]

    def get_progress_percentage(self, obj):
        if obj.total_questions == 0:
            return 0
        answered = obj.attempts.count()
        return round((answered / obj.total_questions) * 100)


class CreateQuizSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, default='')
    mode = serializers.ChoiceField(
        choices=QuizSession.Mode.choices, default=QuizSession.Mode.PRACTICE
    )
    template = serializers.ChoiceField(
        choices=['build_your_own', 'lka_practice', 'exam_practice', 'retry_incorrect'],
        default='build_your_own',
    )
    number_of_questions = serializers.IntegerField(min_value=1, max_value=500, default=50)
    content_areas = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list,
    )
    answer_status = serializers.ChoiceField(
        choices=['all', 'unanswered', 'correct', 'incorrect'],
        default='all', required=False,
    )
    include_saved = serializers.BooleanField(default=False, required=False)
    time_limit_per_question = serializers.IntegerField(
        min_value=0, required=False, allow_null=True, default=None,
    )
    show_explanations = serializers.BooleanField(default=True, required=False)
