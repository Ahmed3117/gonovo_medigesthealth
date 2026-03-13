from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import display

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom admin for MEDIGEST User model.
    Styled with Unfold for a premium admin experience.
    """

    # Unfold forms
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # ── List View ──
    list_display = (
        'display_header', 'role', 'purchased_books_display',
        'is_active', 'created_at_display',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'theme', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    list_per_page = 25
    list_editable = ('role', 'is_active')

    # ── Detail View ──
    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'profile_picture'),
        }),
        ('Role & Display Preferences', {
            'fields': ('role', 'theme', 'font_size'),
            'classes': ('collapse',),
        }),
        ('Notification Preferences', {
            'fields': (
                'email_notifications', 'push_notifications',
                'weekly_reports', 'study_reminders',
            ),
            'classes': ('collapse',),
            'description': 'Figma Settings > Profile tab notification toggles.',
        }),
        ('Learning Goals', {
            'fields': (
                'daily_reading_goal_minutes', 'daily_flashcard_goal',
                'daily_questions_goal',
            ),
            'classes': ('collapse',),
            'description': 'Figma Settings > Preferences tab daily goals.',
        }),
        ('Study Streak', {
            'fields': (
                'current_study_streak', 'longest_study_streak', 'last_study_date',
            ),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # ── Add User View ──
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    # ── Custom Columns ──
    @display(header=True, description="User", ordering="first_name")
    def display_header(self, obj):
        name = obj.get_full_name() or obj.email
        initials = ''
        if obj.first_name and obj.last_name:
            initials = f"{obj.first_name[0]}{obj.last_name[0]}".upper()
        elif obj.email:
            initials = obj.email[0].upper()
        return name, obj.email, initials

    @display(description='Books')
    def purchased_books_display(self, obj):
        return obj.purchased_books_count

    @display(description='Joined', ordering='created_at')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
