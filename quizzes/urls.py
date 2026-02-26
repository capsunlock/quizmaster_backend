from django.urls import path
from .views import QuizListCreateView

urlpatterns = [
    # This handles both GET (listing) and POST (creating)
    path('', QuizListCreateView.as_view(), name='quiz-list-create'),
]