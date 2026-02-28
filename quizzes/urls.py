from django.urls import path
from . import views

urlpatterns = [
    # --- Template Routes (The HTML Pages) ---
    # This acts as the "Traffic Controller" right after login
    path('login-success/', views.login_success_view, name='login-success'),
    
    path('', views.quiz_list_view, name='quiz-list'),
    path('quiz/<int:pk>/', views.quiz_detail_view, name='quiz-detail'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('create-quiz/', views.create_quiz_view, name='create-quiz'),
    path('results/', views.result_view, name='results'),

    # --- API Routes (The Data Endpoints for Fetch) ---
    # These paths are relative to the 'quizzes/' prefix in core/urls.py
    path('api/', views.QuizListCreateView.as_view(), name='api-quiz-list'),
    path('api/submit/', views.AttemptCreateView.as_view(), name='api-quiz-submit'),
    path('api/<int:quiz_id>/leaderboard/', views.LeaderboardView.as_view(), name='api-quiz-leaderboard'),
]