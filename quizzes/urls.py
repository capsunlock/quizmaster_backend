from django.urls import path
from . import views

urlpatterns = [
    # --- Template Routes ---
    path('login-success/', views.login_success_view, name='login-success'),
    path('', views.quiz_list_view, name='quiz-list'),
    path('quiz/<int:pk>/', views.quiz_detail_view, name='quiz-detail'),
    
    path('leaderboard/<int:quiz_id>/', views.leaderboard_view, name='leaderboard'),
    
    path('create-quiz/', views.create_quiz_view, name='create-quiz'),

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    
    path('edit-quiz/<int:quiz_id>/', views.quiz_edit_view, name='quiz-edit'),

    path('results/<int:attempt_id>/', views.quiz_results_view, name='quiz_results'),

    path('my-progress/quiz/<int:quiz_id>/', views.quiz_history_detail, name='quiz-history-detail'),

    # --- API Routes (for JavaScript Fetch) ---
    path('api/', views.QuizListCreateView.as_view(), name='api-quiz-list'),
    path('api/submit-quiz/', views.api_submit_quiz, name='api-submit-quiz'),
    path('api/delete/<int:quiz_id>/', views.api_delete_quiz, name='api-quiz-delete'),
    path('api/<int:pk>/', views.QuizDetailAPIView.as_view(), name='api-quiz-detail'),
    path('api/save-quiz/', views.api_save_quiz, name='api-save-quiz'),
    
    # API Leaderboard 
    path('api/<int:quiz_id>/leaderboard/', views.LeaderboardAPIView.as_view(), name='api-quiz-leaderboard'),
]