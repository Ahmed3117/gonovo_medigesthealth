from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display

from .models import Book, Specialty, Topic, UserBookAccess


# ─────────────────────────────────────────────
# Inline Models
# ─────────────────────────────────────────────

class SpecialtyInline(TabularInline):
    """Inline specialties within a Book admin page."""
    model = Specialty
    extra = 1
    fields = ('name', 'slug', 'icon', 'display_order', 'start_page', 'end_page')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order',)
    show_change_link = True


class TopicInline(StackedInline):
    """Inline topics within a Specialty admin page."""
    model = Topic
    extra = 0
    fields = (
        'title', 'slug', 'display_order',
        'start_page', 'end_page',
        'is_board_basics', 'estimated_tasks',
        'key_points', 'content',
    )
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order',)
    show_change_link = True
    classes = ('collapse',)


# ─────────────────────────────────────────────
# Book Admin
# ─────────────────────────────────────────────

@admin.register(Book)
class BookAdmin(ModelAdmin):
    """
    Admin for managing Books.
    Shows cover image, PDF status, price, and counts of specialties/topics.
    """

    list_display = (
        'display_header', 'product_id', 'price_display',
        'status_badge', 'pdf_badge', 'specialties_count', 'topics_count', 'display_order',
    )
    list_display_links = ('display_header',)
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
        ('PDF Content', {
            'fields': ('pdf_file', 'total_pages', 'estimated_pages'),
            'description': 'Upload the full book PDF. Set total pages for validation. '
                           'Estimated pages is used for progress display.',
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
    @display(header=True, description="Book")
    def display_header(self, obj):
        return obj.title, f"Product: {obj.product_id}", None, (
            {"path": obj.cover_image.url, "squared": True}
            if obj.cover_image else None
        )

    @display(description='Price')
    def price_display(self, obj):
        return f"${obj.price}"

    @display(
        description='Status',
        label={
            'active': 'success',
            'coming_soon': 'warning',
            'archived': 'info',
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @display(description='PDF')
    def pdf_badge(self, obj):
        if obj.has_pdf:
            return f"✓ {obj.total_pages}pp"
        return "—"

    @display(description='Specialties')
    def specialties_count(self, obj):
        return obj.specialty_count

    @display(description='Topics')
    def topics_count(self, obj):
        return obj.topic_count


# ─────────────────────────────────────────────
# Specialty Admin
# ─────────────────────────────────────────────

@admin.register(Specialty)
class SpecialtyAdmin(ModelAdmin):
    """Admin for managing Specialties. Includes inline Topics and page ranges."""

    list_display = (
        'display_header', 'page_range_display', 'topic_count_display',
        'core_badge', 'display_order',
    )
    list_display_links = ('display_header',)
    list_filter = ('book', 'is_core_specialty')
    list_editable = ('display_order',)
    search_fields = ('name', 'book__title')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    ordering = ('book__title', 'display_order')

    fieldsets = (
        (None, {
            'fields': ('book', 'name', 'slug', 'icon', 'description', 'display_order'),
        }),
        ('PDF Page Range', {
            'fields': ('start_page', 'end_page'),
            'description': 'Define which pages in the book PDF belong to this specialty. '
                           'Topic pages must fall within this range.',
        }),
        ('CORE Certification', {
            'fields': ('is_core_specialty', 'core_display_order'),
            'classes': ('collapse',),
            'description': 'Enable if this specialty appears in the CORE certification module.',
        }),
    )

    inlines = [TopicInline]

    @display(header=True, description='Specialty', ordering='name')
    def display_header(self, obj):
        return obj.name, obj.book.title, None

    @display(description='Pages')
    def page_range_display(self, obj):
        if obj.start_page and obj.end_page:
            return f"pp. {obj.start_page}–{obj.end_page} ({obj.page_count}pp)"
        return "—"

    @display(description='Topics')
    def topic_count_display(self, obj):
        return obj.topic_count

    @display(description='CORE')
    def core_badge(self, obj):
        if obj.is_core_specialty:
            return f"✓ Badge #{obj.core_display_order}"
        return "—"


# ─────────────────────────────────────────────
# Topic Admin
# ─────────────────────────────────────────────

@admin.register(Topic)
class TopicAdmin(ModelAdmin):
    """
    Admin for managing Topics — the main content pages.
    Now primarily configured with PDF page ranges.
    CKEditor content is kept for backward compatibility but deprecated.
    """

    list_display = (
        'display_header', 'page_range_display', 'board_basics_badge',
        'display_order', 'updated_at',
    )
    list_display_links = ('display_header',)
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
        ('PDF Page Range', {
            'fields': ('start_page', 'end_page'),
            'description': 'Define which pages in the book PDF belong to this topic. '
                           'Must fall within the parent specialty page range.',
        }),
        ('Key Points', {
            'fields': ('key_points',),
            'description': 'Enter key points as a JSON list: ["Point 1", "Point 2", ...]',
        }),
        ('Settings', {
            'fields': ('is_board_basics', 'estimated_tasks'),
        }),
        ('Legacy Content (Deprecated)', {
            'fields': ('content',),
            'classes': ('collapse',),
            'description': 'This field is deprecated. Content is now delivered via PDF page ranges above. '
                           'Kept for backward compatibility during migration.',
        }),
    )

    @display(header=True, description='Topic', ordering='title')
    def display_header(self, obj):
        return obj.title, f"{obj.specialty.book.title} → {obj.specialty.name}", None

    @display(description='Pages')
    def page_range_display(self, obj):
        if obj.start_page and obj.end_page:
            return f"pp. {obj.start_page}–{obj.end_page} ({obj.page_count}pp)"
        return "—"

    @display(
        description='Board Basics',
        label={True: "info", False: ""},
    )
    def board_basics_badge(self, obj):
        if obj.is_board_basics:
            return True, "✓ Board Basics"
        return False, "—"


# ─────────────────────────────────────────────
# User Book Access Admin
# ─────────────────────────────────────────────

@admin.register(UserBookAccess)
class UserBookAccessAdmin(ModelAdmin):
    """Admin for managing user book access."""

    list_display = (
        'display_header', 'source_badge', 'order_id', 'granted_at',
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

    @display(header=True, description='Access')
    def display_header(self, obj):
        return obj.book.title, obj.user.email, None

    @display(
        description='Source',
        label={
            'webhook': 'warning',
            'manual': 'info',
        },
    )
    def source_badge(self, obj):
        return obj.source, obj.get_source_display()
