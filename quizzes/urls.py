from django.urls import path
from .views import QuizListCreateView, AttemptCreateView 

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list-create'),
    
    # For submitting answers
    path('submit/', AttemptCreateView.as_view(), name='quiz-submit'),
]