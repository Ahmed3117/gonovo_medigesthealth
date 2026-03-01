from django.urls import path

from .views import (
    COREDashboardView,
    CORESpecialtyDetailView,
    BoardBasicsView,
    CMEDashboardView,
    CMECreditHistoryView,
    SubmitCMECreditsView,
    CertificateListView,
    CertificateDownloadView,
)

app_name = 'certificates'

urlpatterns = [
    # ── CORE ────────────────────────────────────────────
    path('core/', COREDashboardView.as_view(), name='core-dashboard'),
    path('core/<slug:specialty_slug>/', CORESpecialtyDetailView.as_view(), name='core-specialty'),

    # ── Board Basics ────────────────────────────────────
    path('board-basics/', BoardBasicsView.as_view(), name='board-basics'),

    # ── CME/MOC ─────────────────────────────────────────
    path('cme/', CMEDashboardView.as_view(), name='cme-dashboard'),
    path('cme/history/', CMECreditHistoryView.as_view(), name='cme-history'),
    path('cme/submit/', SubmitCMECreditsView.as_view(), name='cme-submit'),

    # ── Certificates ────────────────────────────────────
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<uuid:cert_id>/download/', CertificateDownloadView.as_view(), name='certificate-download'),
]
