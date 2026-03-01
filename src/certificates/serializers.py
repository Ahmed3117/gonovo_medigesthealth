from rest_framework import serializers

from certificates.models import (
    CMEActivity, UserCMECredit, CMESubmission,
    UserCOREProgress, Certificate,
)


class CMECreditSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    activity_type = serializers.CharField(
        source='activity.activity_type', read_only=True
    )

    class Meta:
        model = UserCMECredit
        fields = [
            'id', 'activity_title', 'activity_type',
            'credits_earned', 'status', 'credit_year', 'earned_at',
        ]


class CMEDashboardSerializer(serializers.Serializer):
    """CME main dashboard data."""
    earned_credits = serializers.FloatField()
    yearly_cap = serializers.IntegerField(default=300)
    credit_year = serializers.IntegerField()
    credits_by_type = serializers.DictField()
    recent_credits = CMECreditSerializer(many=True)


class COREProgressSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    specialty_icon = serializers.ImageField(source='specialty.icon', read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    correct_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserCOREProgress
        fields = [
            'id', 'specialty_name', 'specialty_icon',
            'badge_status', 'questions_answered', 'questions_correct',
            'progress_percentage', 'correct_percentage',
            'core_quiz_unlocked',
        ]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_type', 'title', 'description',
            'pdf_file', 'credit_year', 'issued_at',
        ]


class CMESubmissionCreateSerializer(serializers.Serializer):
    """Submit earned credits to an accreditation body."""
    accreditation_body = serializers.ChoiceField(
        choices=CMESubmission.AccreditationBody.choices,
    )
    credit_ids = serializers.ListField(
        child=serializers.UUIDField(),
    )
    notes = serializers.CharField(required=False, default='', allow_blank=True)


class CMESubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMESubmission
        fields = [
            'id', 'accreditation_body', 'credits_claimed',
            'credit_year', 'status', 'submitted_at',
        ]
