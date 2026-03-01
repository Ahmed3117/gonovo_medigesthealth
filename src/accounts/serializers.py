from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public user representation — used in login response and profile."""

    purchased_books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'profile_picture',
            'role', 'theme', 'font_size', 'email_notifications',
            'current_study_streak', 'longest_study_streak', 'last_study_date',
            'purchased_books_count', 'created_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Registration — creates user and returns JWT tokens."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Login — extends SimpleJWT to include user profile in response."""

    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        # SimpleJWT handles credential validation and token generation
        data = super().validate(attrs)
        # Attach full user profile to the response
        data['user'] = UserSerializer(self.user).data
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset — accepts email address."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset — uid, token, new password."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Passwords do not match.'}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Change password — requires current password."""

    current_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Profile update — only modifiable fields."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'theme', 'font_size', 'email_notifications']
