from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
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
# 2.5  Password Reset Request (OTP)
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

            # Generate OTP
            from accounts.models import PasswordResetOTP
            otp_obj = PasswordResetOTP.generate_for_user(user)

            # Send OTP email
            from django.core.mail import send_mail
            from django.utils.html import strip_tags

            subject = 'MEDIGEST Health — Your Password Reset Code'
            html_message = f'''
            <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 40px 20px;">
                <div style="background: #ffffff; border-radius: 12px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1a1a2e; font-size: 24px; margin: 0;">MEDIGEST Health</h1>
                        <p style="color: #6c757d; font-size: 14px; margin-top: 5px;">Password Reset Code</p>
                    </div>
                    <p style="color: #333; font-size: 16px; line-height: 1.6;">Hello <strong>{user.first_name or user.email}</strong>,</p>
                    <p style="color: #555; font-size: 15px; line-height: 1.6;">
                        Use the following code to reset your password:
                    </p>
                    <div style="text-align: center; margin: 35px 0;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: #ffffff; padding: 20px 40px;
                                    border-radius: 12px; font-size: 36px; font-weight: 700;
                                    letter-spacing: 8px; display: inline-block;">
                            {otp_obj.otp}
                        </div>
                    </div>
                    <p style="color: #888; font-size: 13px; line-height: 1.5; text-align: center;">
                        This code expires in <strong>10 minutes</strong>.<br>
                        If you didn't request this, you can safely ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
                    <p style="color: #aaa; font-size: 12px; text-align: center;">
                        &copy; 2026 MEDIGEST Health. All rights reserved.
                    </p>
                </div>
            </div>
            '''
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

        except User.DoesNotExist:
            pass  # Security: don't reveal whether email exists

        return Response(
            {'detail': f'If {email} is registered, a password reset code has been sent.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────
# 2.6  Password Reset Confirm (OTP)
# ─────────────────────────────────────────────
class PasswordResetConfirmView(APIView):
    """POST /api/v1/auth/password/reset/confirm/"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_code = serializer.validated_data['otp']

        from accounts.models import PasswordResetOTP
        otp_obj = PasswordResetOTP.objects.filter(
            otp=otp_code, is_used=False,
        ).order_by('-created_at').first()

        if not otp_obj or not otp_obj.is_valid:
            return Response(
                {'detail': 'Invalid or expired OTP code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user = otp_obj.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        return Response({'detail': 'Password has been reset successfully.'})


# ─────────────────────────────────────────────
# 12.1  Get / Update Current User Profile
# ─────────────────────────────────────────────
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/users/me/  — current user profile
    PATCH /api/v1/users/me/ — update profile fields (supports profile_picture upload)
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
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
