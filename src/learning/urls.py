from django.urls import path

from .views import (
    DashboardView,
    LearningPlanView,
    AvailableTopicsView,
    AddLearningPlanTopicView,
    RemoveLearningPlanTopicView,
    RecordStudySessionView,
)

app_name = 'learning'

urlpatterns = [
    # ── Dashboard ───────────────────────────────────────
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # ── Learning Plan ───────────────────────────────────
    path('learning-plan/', LearningPlanView.as_view(), name='plan'),
    path('learning-plan/available-topics/', AvailableTopicsView.as_view(), name='available-topics'),
    path('learning-plan/topics/', AddLearningPlanTopicView.as_view(), name='add-topic'),
    path('learning-plan/topics/<uuid:entry_id>/', RemoveLearningPlanTopicView.as_view(), name='remove-topic'),

    # ── Study Sessions ──────────────────────────────────
    path('users/me/study-sessions/', RecordStudySessionView.as_view(), name='record-session'),
]
