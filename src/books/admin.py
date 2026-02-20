from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count

from .models import Book, Specialty, Topic, UserBookAccess


# ─────────────────────────────────────────────
# Inline Models
# ─────────────────────────────────────────────

class SpecialtyInline(admin.TabularInline):
    """Inline specialties within a Book admin page."""
    model = Specialty
    extra = 1
    fields = ('name', 'slug', 'icon', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order',)
    show_change_link = True


class TopicInline(admin.StackedInline):
    """Inline topics within a Specialty admin page."""
    model = Topic
    extra = 0
    fields = ('title', 'slug', 'display_order', 'is_board_basics', 'key_points', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order',)
    show_change_link = True
    classes = ('collapse',)


# ─────────────────────────────────────────────
# Book Admin
# ─────────────────────────────────────────────

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin for managing Books.
    Shows cover image, status badge, and counts of specialties/topics.
    Includes inline Specialties.
    """

    list_display = (
        'cover_thumbnail', 'title', 'product_id', 'price_display',
        'status_badge', 'specialties_count', 'topics_count', 'display_order',
    )
    list_display_links = ('title',)
    list_filter = ('status',)
    list_editable = ('display_order',)
    search_fields = ('title', 'product_id')
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    ordering = ('display_order',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'product_id', 'cover_image'),
        }),
        ('Pricing & Status', {
            'fields': ('price', 'status', 'display_order'),
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
    )

    inlines = [SpecialtyInline]

    # ── Custom Columns ──
    @admin.display(description='Cover')
    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:40px; height:55px; object-fit:cover; '
                'border-radius:4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />',
                obj.cover_image.url
            )
        return mark_safe(
            '<div style="width:40px; height:55px; background:#E5E7EB; '
            'border-radius:4px; display:flex; align-items:center; '
            'justify-content:center; font-size:16px;">📚</div>'
        )

    @admin.display(description='Price')
    def price_display(self, obj):
        return format_html('<strong>${}</strong>', obj.price)

    @admin.display(description='Status')
    def status_badge(self, obj):
        colors = {
            'active': ('#059669', '#D1FAE5'),
            'coming_soon': ('#D97706', '#FEF3C7'),
            'archived': ('#6B7280', '#F3F4F6'),
        }
        fg, bg = colors.get(obj.status, ('#6B7280', '#F3F4F6'))
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 10px; '
            'border-radius:12px; font-size:11px; font-weight:600;">{}</span>',
            bg, fg, label
        )

    @admin.display(description='Specialties')
    def specialties_count(self, obj):
        count = obj.specialty_count
        return format_html(
            '<span style="font-weight:600;">{}</span>', count
        )

    @admin.display(description='Topics')
    def topics_count(self, obj):
        count = obj.topic_count
        return format_html(
            '<span style="font-weight:600;">{}</span>', count
        )


# ─────────────────────────────────────────────
# Specialty Admin
# ─────────────────────────────────────────────

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """
    Admin for managing Specialties.
    Includes inline Topics.
    """

    list_display = (
        'name', 'book_title', 'topic_count_display', 'display_order',
    )
    list_display_links = ('name',)
    list_filter = ('book',)
    list_editable = ('display_order',)
    search_fields = ('name', 'book__title')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    ordering = ('book__title', 'display_order')

    fieldsets = (
        (None, {
            'fields': ('book', 'name', 'slug', 'icon', 'description', 'display_order'),
        }),
    )

    inlines = [TopicInline]

    @admin.display(description='Book', ordering='book__title')
    def book_title(self, obj):
        return obj.book.title

    @admin.display(description='Topics')
    def topic_count_display(self, obj):
        count = obj.topic_count
        return format_html('<strong>{}</strong>', count)


# ─────────────────────────────────────────────
# Topic Admin
# ─────────────────────────────────────────────

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Admin for managing Topics — the main content pages.
    Uses CKEditor for rich HTML content editing.
    """

    list_display = (
        'title', 'specialty_name', 'book_name',
        'board_basics_badge', 'display_order', 'updated_at',
    )
    list_display_links = ('title',)
    list_filter = (
        'is_board_basics',
        'specialty__book',
        'specialty',
    )
    list_editable = ('display_order',)
    search_fields = ('title', 'specialty__name', 'specialty__book__title')
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 25
    ordering = ('specialty__book__title', 'specialty__display_order', 'display_order')

    fieldsets = (
        ('Location', {
            'fields': ('specialty', 'title', 'slug', 'display_order'),
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',),
            'description': 'Use the rich text editor below to add the full topic content. '
                           'Supports headings, bold, images, tables, and clinical photos.',
        }),
        ('Key Points', {
            'fields': ('key_points',),
            'description': 'Enter key points as a JSON list: ["Point 1", "Point 2", ...]',
        }),
        ('Settings', {
            'fields': ('is_board_basics',),
        }),
    )

    @admin.display(description='Specialty', ordering='specialty__name')
    def specialty_name(self, obj):
        return obj.specialty.name

    @admin.display(description='Book', ordering='specialty__book__title')
    def book_name(self, obj):
        return obj.specialty.book.title

    @admin.display(description='Board Basics')
    def board_basics_badge(self, obj):
        if obj.is_board_basics:
            return mark_safe(
                '<span style="background:#DBEAFE; color:#1D4ED8; padding:2px 8px; '
                'border-radius:10px; font-size:11px; font-weight:600;">✓ BB</span>'
            )
        return mark_safe('<span style="color:#D1D5DB;">—</span>')


# ─────────────────────────────────────────────
# User Book Access Admin
# ─────────────────────────────────────────────

@admin.register(UserBookAccess)
class UserBookAccessAdmin(admin.ModelAdmin):
    """
    Admin for managing user book access.
    Allows admins to manually grant/revoke book access.
    """

    list_display = (
        'user_email', 'book_title', 'source_badge', 'order_id', 'granted_at',
    )
    list_filter = ('source', 'book', 'granted_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'book__title', 'order_id')
    raw_id_fields = ('user',)
    autocomplete_fields = ('book',)
    list_per_page = 25
    ordering = ('-granted_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'book', 'order_id', 'source'),
        }),
    )

    @admin.display(description='User', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Book', ordering='book__title')
    def book_title(self, obj):
        return obj.book.title

    @admin.display(description='Source')
    def source_badge(self, obj):
        if obj.source == 'webhook':
            return mark_safe(
                '<span style="background:#FEF3C7; color:#D97706; padding:2px 8px; '
                'border-radius:10px; font-size:11px; font-weight:600;">⚡ Webhook</span>'
            )
        return mark_safe(
            '<span style="background:#E0E7FF; color:#4338CA; padding:2px 8px; '
            'border-radius:10px; font-size:11px; font-weight:600;">👤 Manual</span>'
        )
