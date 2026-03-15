from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FAQCategory, ContactMethod
from .serializers import FAQCategorySerializer, ContactMethodSerializer

class HelpCenterView(APIView):
    """
    Returns data for the Help Center page.
    Includes grouped FAQs and available Contact Methods.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = FAQCategory.objects.all().order_by('display_order')
        contact_methods = ContactMethod.objects.all().order_by('display_order')

        return Response({
            'faq_categories': FAQCategorySerializer(categories, many=True).data,
            'contact_methods': ContactMethodSerializer(contact_methods, many=True).data,
        })
