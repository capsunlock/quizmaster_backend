from django.urls import path
from . import views

urlpatterns = [
    # --- Template Routes ---
    path('login-success/', views.login_success_view, name='login-success'),
    path('', views.quiz_list_view, name='quiz-list'),
    path('quiz/<int:pk>/', views.quiz_detail_view, name='quiz-detail'),
    
    # Updated: Leaderboard now requires a quiz_id to show specific rankings
    path('leaderboard/<int:quiz_id>/', views.leaderboard_view, name='leaderboard'),
    
    path('create-quiz/', views.create_quiz_view, name='create-quiz'),
    
    # New: Route for the Teacher's Edit Interface
    path('edit-quiz/<int:quiz_id>/', views.quiz_edit_view, name='quiz-edit'),

    # Updated: Removed the generic 'results/' and kept the specific ID route
    path('results/<int:attempt_id>/', views.quiz_results_view, name='quiz_results'),

    # --- API Routes (for JavaScript Fetch) ---
    path('api/', views.QuizListCreateView.as_view(), name='api-quiz-list'),
    path('api/submit/', views.api_submit_quiz, name='api-quiz-submit'),
    path('api/delete/<int:quiz_id>/', views.api_delete_quiz, name='api-quiz-delete'),
    path('api/<int:pk>/', views.QuizDetailAPIView.as_view(), name='api-quiz-detail'),
    
    # API Leaderboard also updated to match the view's name
    path('api/<int:quiz_id>/leaderboard/', views.LeaderboardAPIView.as_view(), name='api-quiz-leaderboard'),
]