from django.urls import path

from .views import (
    FlashcardDecksView,
    FlashcardByPositionView,
    ReviewFlashcardView,
)

app_name = 'flashcards'

urlpatterns = [
    path('flashcards/', FlashcardDecksView.as_view(), name='decks'),
    path('flashcards/decks/<slug:book_slug>/<int:position>/', FlashcardByPositionView.as_view(), name='by-position'),
    path('flashcards/<uuid:flashcard_id>/review/', ReviewFlashcardView.as_view(), name='review'),
]
