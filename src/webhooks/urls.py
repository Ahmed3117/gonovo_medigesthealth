from django.urls import path

from .views import PurchaseWebhookView

app_name = 'webhooks'

urlpatterns = [
    path('webhooks/purchase/', PurchaseWebhookView.as_view(), name='purchase'),
]
