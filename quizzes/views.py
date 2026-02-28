from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Quiz, Attempt 
from .serializers import (
    QuizSerializer, 
    StudentQuizSerializer, 
    AttemptSerializer, 
    LeaderboardSerializer
)

# --- CUSTOM PERMISSION ---
class IsTeacher(permissions.BasePermission):
    """ Only allows teachers to perform 'Write' actions (POST) """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_teacher

# --- API VIEWS (For JavaScript Fetch calls) ---

class QuizListCreateView(generics.ListCreateAPIView): 
    queryset = Quiz.objects.all()
    permission_classes = [IsTeacher] # Attached our security here
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['creator__username']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.user.is_teacher:
            return QuizSerializer
        return StudentQuizSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class AttemptCreateView(generics.CreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        return Attempt.objects.filter(quiz_id=quiz_id).order_by('-score', 'completed_at')

# --- TEMPLATE VIEWS (For Rendering HTML) ---

def is_teacher_check(user):
    return user.is_authenticated and user.is_teacher

def quiz_list_view(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quiz_detail.html', {'quiz': quiz})

@login_required
def login_success_view(request):
    """
    Redirects users based on their role after a successful login.
    """
    if request.user.is_teacher:
        return redirect('create-quiz')
    else:
        return redirect('quiz-list')
    
@user_passes_test(is_teacher_check, login_url='quiz-list', redirect_field_name=None)
def create_quiz_view(request):
    return render(request, 'create_quiz.html')

def leaderboard_view(request):
    attempts = Attempt.objects.select_related('student').order_by('-score')[:10]
    return render(request, 'leaderboard.html', {'attempts': attempts})

def result_view(request):
    return render(request, 'result.html')