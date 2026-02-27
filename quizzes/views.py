from django.shortcuts import render
from rest_framework import generics, permissions, filters
from .models import Quiz, Attempt 
from .serializers import QuizSerializer, StudentQuizSerializer, AttemptSerializer, LeaderboardSerializer 
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

# Custom Permission to check if user is a teacher
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher

class QuizListCreateView(generics.ListCreateAPIView): 
    # Teachers can Create, everyone (authenticated) can List
    queryset = Quiz.objects.all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['creator__username'] # Filter by teacher name
    search_fields = ['title', 'description'] # Search by words in title/desc
    ordering_fields = ['created_at'] # Sort by date
    ordering = ['-created_at'] # Default to newest first
    
    def get_serializer_class(self):
        # If the user is a teacher, show them everything (including answers)
        if self.request.user.is_teacher:
            return QuizSerializer
        # If student, show them the "Exam Paper" version
        return StudentQuizSerializer

    def perform_create(self, serializer):
        # Automatically set the creator to the logged-in teacher
        serializer.save(creator=self.request.user)

class AttemptCreateView(generics.CreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # This ensures the score is calculated for the logged-in student
        serializer.save(student=self.request.user)

class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Grab the quiz_id from the URL (e.g., /api/quizzes/1/leaderboard/)
        quiz_id = self.kwargs['quiz_id']
        # Order by Score (Descending) and then by Date (Ascending)
        return Attempt.objects.filter(quiz_id=quiz_id).order_by('-score', 'completed_at')