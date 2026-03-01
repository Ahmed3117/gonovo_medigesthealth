from django.urls import path

from .views import (
    QuestionBankMainView,
    QuestionSetDetailView,
    AnsweredQuestionsView,
    SavedQuestionsView,
    ToggleSaveQuestionView,
    CustomQuizListView,
    CreateCustomQuizView,
    DeleteCustomQuizView,
    QuestionDetailView,
    SubmitAnswerView,
    ShuffleQuestionsView,
)

app_name = 'questions'

urlpatterns = [
    path('question-bank/', QuestionBankMainView.as_view(), name='main'),
    path('question-bank/sets/<slug:book_slug>/', QuestionSetDetailView.as_view(), name='set-detail'),
    path('question-bank/answered/', AnsweredQuestionsView.as_view(), name='answered'),
    path('question-bank/saved/', SavedQuestionsView.as_view(), name='saved'),
    path('question-bank/questions/<uuid:question_id>/toggle-save/', ToggleSaveQuestionView.as_view(), name='toggle-save'),
    path('question-bank/custom-quizzes/', CustomQuizListView.as_view(), name='custom-quizzes'),
    path('question-bank/custom-quizzes/create/', CreateCustomQuizView.as_view(), name='create-quiz'),
    path('question-bank/custom-quizzes/<uuid:quiz_id>/', DeleteCustomQuizView.as_view(), name='delete-quiz'),
    path('question-bank/questions/<uuid:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('question-bank/questions/<uuid:question_id>/answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('question-bank/shuffle/', ShuffleQuestionsView.as_view(), name='shuffle'),
]
