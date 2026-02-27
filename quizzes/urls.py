from django.urls import path
from .views import QuizListCreateView, AttemptCreateView, LeaderboardView

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list-create'),
    # For submitting answers
    path('submit/', AttemptCreateView.as_view(), name='quiz-submit'),
    # Leaderboard Route
    path('<int:quiz_id>/leaderboard/', LeaderboardView.as_view(), name='quiz-leaderboard'),
]