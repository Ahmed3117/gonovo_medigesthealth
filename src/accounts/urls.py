from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView,
    ChangePasswordView,
    DeleteAccountView,
)

app_name = 'accounts'

urlpatterns = [
    # ── Auth ────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # ── User Profile ───────────────────────────────────
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/me/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
