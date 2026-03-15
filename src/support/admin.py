from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import FAQCategory, FAQ, ContactMethod

class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1

@admin.register(FAQCategory)
class FAQCategoryAdmin(ModelAdmin):
    list_display = ('name', 'display_order', 'faq_count')
    search_fields = ('name',)
    list_editable = ('display_order',)
    inlines = [FAQInline]

    @display(description='FAQs')
    def faq_count(self, obj):
        return obj.faqs.count()

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('question', 'category_name', 'is_published', 'display_order')
    list_filter = ('is_published', 'category')
    search_fields = ('question', 'answer')
    list_editable = ('is_published', 'display_order')
    list_per_page = 25

    @display(description='Category', ordering='category__display_order')
    def category_name(self, obj):
        return obj.category.name

@admin.register(ContactMethod)
class ContactMethodAdmin(ModelAdmin):
    list_display = ('subtitle', 'title', 'icon_type', 'display_order')
    search_fields = ('title', 'subtitle', 'action_url')
    list_editable = ('display_order',)
    list_filter = ('icon_type',)
    fieldsets = (
        ('Contact Information', {
            'fields': ('title', 'subtitle', 'icon_type'),
            'description': 'Main info shown on the card.',
        }),
        ('Action / Link', {
            'fields': ('action_text', 'action_url'),
            'description': 'E.g., "Speak with a specialist ->" pointing to "tel:18001234567"',
        }),
        ('Settings', {
            'fields': ('display_order',),
        }),
    )
