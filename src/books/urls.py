from django.urls import path

from .views import (
    MyBooksView,
    StoreBooksView,
    BookDetailView,
    BookmarkListCreateView,
    BookmarkDeleteView,
    NotesHighlightsListView,
    NotesHighlightsDetailView,
    HighlightCreateView,
    HighlightDeleteView,
    NoteCreateView,
    NoteUpdateView,
    NoteDeleteView,
    TopicDetailView,
    TopicProgressUpdateView,
)

app_name = 'books'

urlpatterns = [
    # ── Syllabus ────────────────────────────────────────
    path('syllabus/my-books/', MyBooksView.as_view(), name='my-books'),
    path('syllabus/store/', StoreBooksView.as_view(), name='store'),
    path('syllabus/books/<slug:book_slug>/', BookDetailView.as_view(), name='book-detail'),

    # ── Bookmarks ───────────────────────────────────────
    path('syllabus/bookmarks/', BookmarkListCreateView.as_view(), name='bookmark-list-create'),
    path('syllabus/bookmarks/<uuid:bookmark_id>/', BookmarkDeleteView.as_view(), name='bookmark-delete'),

    # ── Notes & Highlights ──────────────────────────────
    path('syllabus/notes-highlights/', NotesHighlightsListView.as_view(), name='notes-highlights-list'),
    path('syllabus/notes-highlights/<uuid:topic_id>/', NotesHighlightsDetailView.as_view(), name='notes-highlights-detail'),
    path('syllabus/highlights/', HighlightCreateView.as_view(), name='highlight-create'),
    path('syllabus/highlights/<uuid:highlight_id>/', HighlightDeleteView.as_view(), name='highlight-delete'),
    path('syllabus/notes/', NoteCreateView.as_view(), name='note-create'),
    path('syllabus/notes/<uuid:note_id>/', NoteUpdateView.as_view(), name='note-update'),
    path('syllabus/notes/<uuid:note_id>/delete/', NoteDeleteView.as_view(), name='note-delete'),

    # ── Reading Interface ───────────────────────────────
    path('syllabus/topics/<slug:topic_slug>/', TopicDetailView.as_view(), name='topic-detail'),
    path('syllabus/topics/<slug:topic_slug>/progress/', TopicProgressUpdateView.as_view(), name='topic-progress'),
]
