from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Quiz
from .serializers import QuizSerializer, StudentQuizSerializer

# Create your views here.

# Custom Permission to check if user is a teacher
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher

class QuizListCreateView(generics.ListCreateAPIView): 
    # Teachers can Create, everyone (authenticated) can List
    queryset = Quiz.objects.all()
    
    def get_serializer_class(self):
        # If the user is a teacher, show them everything (including answers)
        if self.request.user.is_teacher:
            return QuizSerializer
        # If student, show them the "Exam Paper" version
        return StudentQuizSerializer

    def perform_create(self, serializer):
        # Automatically set the creator to the logged-in teacher
        serializer.save(creator=self.request.user)