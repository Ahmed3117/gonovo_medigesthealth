from django.urls import path
from .views import HelpCenterView

app_name = 'support'

urlpatterns = [
    path('', HelpCenterView.as_view(), name='help_center'),
]
