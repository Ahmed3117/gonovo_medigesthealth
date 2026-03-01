from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Specialty
from certificates.models import (
    CMEActivity, UserCMECredit, CMESubmission,
    UserCOREProgress, Certificate,
)
from .serializers import (
    CMECreditSerializer,
    COREProgressSerializer,
    CertificateSerializer,
    CMESubmissionCreateSerializer,
    CMESubmissionSerializer,
)


# ═════════════════════════════════════════════
# 8.1  CORE Dashboard
# ═════════════════════════════════════════════
class COREDashboardView(APIView):
    """GET /api/v1/core/"""

    def get(self, request):
        user = request.user

        # Get or create progress for all CORE specialties
        core_specialties = Specialty.objects.filter(
            is_core_specialty=True,
        ).order_by('core_display_order')

        badges = []
        for spec in core_specialties:
            progress, _ = UserCOREProgress.objects.get_or_create(
                user=user, specialty=spec,
            )
            badges.append(progress)

        completed = sum(1 for b in badges if b.badge_status == UserCOREProgress.BadgeStatus.COMPLETED)
        total = len(badges)

        serializer = COREProgressSerializer(badges, many=True)

        return Response({
            'overall_progress': {
                'completed_badges': completed,
                'total_badges': total,
                'percentage': round((completed / total) * 100) if total else 0,
            },
            'badges': serializer.data,
        })


# ═════════════════════════════════════════════
# 8.2  CORE Specialty Detail
# ═════════════════════════════════════════════
class CORESpecialtyDetailView(APIView):
    """GET /api/v1/core/{specialty_slug}/"""

    def get(self, request, specialty_slug):
        spec = Specialty.objects.filter(
            slug=specialty_slug, is_core_specialty=True,
        ).first()
        if not spec:
            return Response(
                {'detail': 'Specialty not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        progress, _ = UserCOREProgress.objects.get_or_create(
            user=request.user, specialty=spec,
        )

        return Response({
            'specialty': {
                'id': str(spec.id),
                'name': spec.name,
                'icon': spec.icon.url if spec.icon else None,
            },
            'badge_status': progress.badge_status,
            'questions_answered': progress.questions_answered,
            'questions_correct': progress.questions_correct,
            'last_30_correct': progress.last_30_correct,
            'last_30_total': progress.last_30_total,
            'core_quiz_unlocked': progress.core_quiz_unlocked,
            'progress_percentage': progress.progress_percentage,
            'correct_percentage': progress.correct_percentage,
        })


# ═════════════════════════════════════════════
# 9.1  Board Basics List
# ═════════════════════════════════════════════
class BoardBasicsView(APIView):
    """GET /api/v1/board-basics/"""

    def get(self, request):
        from books.models import Topic
        from learning.models import UserTopicProgress

        topics = Topic.objects.filter(
            is_board_basics=True,
        ).select_related('specialty').order_by('specialty__name', 'display_order')

        # Group by specialty
        specialty_map = {}
        for topic in topics:
            spec_id = str(topic.specialty.id)
            if spec_id not in specialty_map:
                specialty_map[spec_id] = {
                    'id': spec_id,
                    'name': topic.specialty.name,
                    'topics': [],
                }

            progress = UserTopicProgress.objects.filter(
                user=request.user, topic=topic,
            ).first()

            specialty_map[spec_id]['topics'].append({
                'id': str(topic.id),
                'title': topic.title,
                'slug': topic.slug,
                'is_completed': progress.is_completed if progress else False,
            })

        specialties = list(specialty_map.values())
        total_topics = sum(len(s['topics']) for s in specialties)
        completed = sum(
            1 for s in specialties for t in s['topics'] if t['is_completed']
        )

        return Response({
            'overall_progress': {
                'completed': completed,
                'total': total_topics,
                'percentage': round((completed / total_topics) * 100) if total_topics else 0,
            },
            'specialties': specialties,
        })


# ═════════════════════════════════════════════
# 11.1  CME/MOC Dashboard
# ═════════════════════════════════════════════
class CMEDashboardView(APIView):
    """GET /api/v1/cme/"""

    def get(self, request):
        user = request.user
        year = timezone.now().year

        credits = UserCMECredit.objects.filter(user=user, credit_year=year)
        total_earned = credits.aggregate(
            total=Sum('credits_earned')
        )['total'] or 0

        # Credits by type
        by_type = {}
        for at in CMEActivity.ActivityType.choices:
            type_credits = credits.filter(
                activity__activity_type=at[0],
            ).aggregate(t=Sum('credits_earned'))['t'] or 0
            by_type[at[0]] = round(float(type_credits), 2)

        recent = credits.order_by('-earned_at')[:10]

        return Response({
            'earned_credits': round(float(total_earned), 2),
            'yearly_cap': 300,
            'credit_year': year,
            'credits_by_type': by_type,
            'recent_credits': CMECreditSerializer(recent, many=True).data,
        })


# ═════════════════════════════════════════════
# 11.2  CME Credit History
# ═════════════════════════════════════════════
class CMECreditHistoryView(generics.ListAPIView):
    """GET /api/v1/cme/history/"""

    serializer_class = CMECreditSerializer

    def get_queryset(self):
        qs = UserCMECredit.objects.filter(
            user=self.request.user,
        ).select_related('activity')

        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(credit_year=int(year))

        activity_type = self.request.query_params.get('type')
        if activity_type:
            qs = qs.filter(activity__activity_type=activity_type)

        return qs


# ═════════════════════════════════════════════
# 11.3  Submit CME Credits
# ═════════════════════════════════════════════
class SubmitCMECreditsView(APIView):
    """POST /api/v1/cme/submit/"""

    def post(self, request):
        serializer = CMESubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        credits = UserCMECredit.objects.filter(
            user=request.user, id__in=d['credit_ids'],
        )
        total = credits.aggregate(t=Sum('credits_earned'))['t'] or 0

        submission = CMESubmission.objects.create(
            user=request.user,
            accreditation_body=d['accreditation_body'],
            credits_claimed=total,
            credit_year=timezone.now().year,
        )
        submission.credits.set(credits)

        # Mark credits as submitted
        credits.update(status=UserCMECredit.Status.SUBMITTED)

        return Response(
            CMESubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


# ═════════════════════════════════════════════
# 11.4  Certificates
# ═════════════════════════════════════════════
class CertificateListView(generics.ListAPIView):
    """GET /api/v1/certificates/"""

    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user)


class CertificateDownloadView(APIView):
    """GET /api/v1/certificates/{cert_id}/download/"""

    def get(self, request, cert_id):
        from django.http import FileResponse
        cert = Certificate.objects.filter(
            id=cert_id, user=request.user,
        ).first()
        if not cert or not cert.pdf_file:
            return Response(
                {'detail': 'Certificate not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            cert.pdf_file.open('rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f'{cert.title}.pdf',
        )
