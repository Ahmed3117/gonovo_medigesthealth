from rest_framework import serializers
from .models import FAQCategory, FAQ, ContactMethod

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']

class FAQCategorySerializer(serializers.ModelSerializer):
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'faqs']

    def get_faqs(self, obj):
        # Only return published FAQs ordered correctly
        qs = obj.faqs.filter(is_published=True).order_by('display_order')
        return FAQSerializer(qs, many=True).data

class ContactMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMethod
        fields = ['id', 'title', 'subtitle', 'icon_type', 'action_text', 'action_url']
