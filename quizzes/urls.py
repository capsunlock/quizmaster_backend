from django.urls import path
from . import views

urlpatterns = [
    # --- Template Routes ---
    path('login-success/', views.login_success_view, name='login-success'),
    path('', views.quiz_list_view, name='quiz-list'),
    path('quiz/<int:pk>/', views.quiz_detail_view, name='quiz-detail'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('create-quiz/', views.create_quiz_view, name='create-quiz'),
    path('results/', views.result_view, name='results'),
    path('results/<int:attempt_id>/', views.quiz_results_view, name='quiz-results'),

    # --- API Routes ---
    path('api/', views.QuizListCreateView.as_view(), name='api-quiz-list'),
    path('api/submit/', views.api_submit_quiz, name='api-quiz-submit'),
    path('api/<int:quiz_id>/leaderboard/', views.LeaderboardView.as_view(), name='api-quiz-leaderboard'),
]