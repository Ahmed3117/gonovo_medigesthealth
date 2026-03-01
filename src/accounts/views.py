from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


# ─────────────────────────────────────────────
# 2.1  Register
# ─────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for auto-login after registration
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────
# 2.2  Login (extends SimpleJWT)
# ─────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/"""

    serializer_class = LoginSerializer


# ─────────────────────────────────────────────
# 2.4  Logout
# ─────────────────────────────────────────────
class LogoutView(APIView):
    """POST /api/v1/auth/logout/ — blacklists the refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'detail': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'})
        except Exception:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ─────────────────────────────────────────────
# 2.5  Password Reset Request
# ─────────────────────────────────────────────
class PasswordResetRequestView(APIView):
    """POST /api/v1/auth/password/reset/"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # TODO: Send email with reset link containing uid/token
            # For now, log the token (in production, send via email service)
            print(f'[Password Reset] uid={uid} token={token}')
        except User.DoesNotExist:
            pass  # Security: always return 200

        return Response(
            {'detail': f'Password reset instructions sent to {email}'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────
# 2.6  Password Reset Confirm
# ─────────────────────────────────────────────
class PasswordResetConfirmView(APIView):
    """POST /api/v1/auth/password/reset/confirm/"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data['token']
        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password has been reset successfully.'})


# ─────────────────────────────────────────────
# 12.1  Get / Update Current User Profile
# ─────────────────────────────────────────────
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/users/me/  — current user profile
    PATCH /api/v1/users/me/ — update profile fields
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UserUpdateSerializer
        return UserSerializer


# ─────────────────────────────────────────────
# 12.3  Change Password
# ─────────────────────────────────────────────
class ChangePasswordView(APIView):
    """POST /api/v1/users/me/change-password/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password changed successfully.'})
