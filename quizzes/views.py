import json
import traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone 
from datetime import timedelta
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Quiz, Attempt, AttemptAnswer, Choice, Question
from .serializers import (
    QuizSerializer, 
    StudentQuizSerializer, 
    AttemptSerializer, 
    LeaderboardSerializer
)
from django.db.models import Avg, Count


# --- CUSTOM PERMISSION & HELPER ---
class IsTeacher(permissions.BasePermission):
    """ Only allows teachers to perform 'Write' actions (POST/PUT/DELETE) """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_teacher

def is_teacher_check(user):
    return user.is_authenticated and user.is_teacher

# --- API VIEWS (For JavaScript Fetch calls) ---

class QuizListCreateView(generics.ListCreateAPIView): 
    queryset = Quiz.objects.all()
    permission_classes = [IsTeacher]
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

class LeaderboardAPIView(generics.ListAPIView):
    """ API endpoint for Leaderboard data """
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        return Attempt.objects.filter(quiz_id=quiz_id).order_by('-score', '-completed_at')[:10]
    
class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint to Get, Update, or Delete a specific quiz """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Quiz.objects.filter(creator=self.request.user)
        return Quiz.objects.all()

# --- TEMPLATE VIEWS (For Rendering HTML) ---

@login_required
def quiz_list_view(request):
    quizzes = Quiz.objects.all().order_by('-created_at')
    recent_cutoff = timezone.now() - timedelta(hours=24)
    
    return render(request, 'quizzes/quiz_list.html', { 
        'quizzes': quizzes,
        'recent_cutoff': recent_cutoff
    })

@login_required
def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})

@login_required
def leaderboard_view(request, quiz_id):
    """ Renders the leaderboard for a SPECIFIC quiz """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = Attempt.objects.filter(quiz=quiz).select_related('student').order_by('-score', '-completed_at')[:10]
    return render(request, 'quizzes/leaderboard.html', {
        'quiz': quiz,
        'attempts': attempts
    })

@login_required
@user_passes_test(is_teacher_check, login_url='quiz-list')
def create_quiz_view(request):
    return render(request, 'quizzes/create_quiz.html')

@login_required
def quiz_edit_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not request.user.is_teacher or quiz.creator != request.user:
        raise PermissionDenied("You can only edit quizzes you created.")
    
    return render(request, 'quizzes/quiz_edit.html', {'quiz': quiz})

@login_required
def quiz_results_view(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    if not request.user.is_teacher and attempt.student != request.user:
        raise PermissionDenied
    
    return render(request, 'quizzes/quiz_results.html', {
        'attempt': attempt
    })

@login_required
def login_success_view(request):
    if request.user.is_teacher:
        return redirect('create-quiz')
    return redirect('quiz-list')

# --- AJAX / FETCH ENDPOINTS ---

@csrf_protect
@login_required
@user_passes_test(is_teacher_check)
def api_save_quiz(request):
    """
    Expects JSON structure:
    {
        "title": "Quiz Title",
        "description": "...",
        "time_limit": 30,
        "questions": [
            {
                "text": "Question 1?",
                "choices": [
                    {"text": "Ans A", "is_correct": true},
                    {"text": "Ans B", "is_correct": false}
                ]
            }
        ]
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 1. Create the Quiz
            quiz = Quiz.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                time_limit=data.get('time_limit', 30),
                creator=request.user
            )

            # 2. Create Questions and Choices
            for q_data in data.get('questions', []):
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data.get('text')
                )
                for c_data in q_data.get('choices', []):
                    Choice.objects.create(
                        question=question,
                        text=c_data.get('text'),
                        is_correct=c_data.get('is_correct', False)
                    )

            return JsonResponse({'message': 'Quiz created successfully!', 'quiz_id': quiz.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_protect
@login_required
def api_submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quiz')
            answers_data = data.get('answers')
            
            quiz = get_object_or_404(Quiz, id=quiz_id)
            # Create the attempt record for the student
            attempt = Attempt.objects.create(student=request.user, quiz=quiz)
            
            correct_count = 0
            questions = quiz.questions.all()
            total_questions = questions.count()

            for item in answers_data:
                question = get_object_or_404(Question, id=item['question'])
                choice_id = item.get('selected_choice')

                # Check if the student actually picked something
                if choice_id:
                    selected_choice = get_object_or_404(Choice, id=choice_id)
                    
                    AttemptAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=selected_choice
                    )
                    
                    if selected_choice.is_correct:
                        correct_count += 1
                else:
                    # Time ran out or skipped: record the question but no choice
                    AttemptAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=None
                    )

            # Final Score Calculation
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            attempt.score = round(score, 2)
            attempt.save()

            return JsonResponse({'score': attempt.score, 'attempt_id': attempt.id})
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def api_delete_quiz(request, quiz_id):
    if request.method == 'DELETE':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if quiz.creator == request.user:
            quiz.delete()
            return JsonResponse({'message': 'Deleted successfully'}, status=200)
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
@login_required
def teacher_dashboard(request):
    # Only allow teachers (is_staff) to see this
    if not request.user.is_staff:
        return render(request, 'quizzes/403.html') # Or redirect to home

    # 1. Fetch quizzes created by the logged-in user
    # 2. Annotate adds 'num_attempts' and 'avg_score' as virtual fields on each quiz object
    quizzes = Quiz.objects.filter(creator=request.user).annotate(
        num_attempts=Count('attempts'),
        avg_score=Avg('attempts__score')
    ).order_by('-created_at')

    # 3. Calculate Global Stats for the top cards
    total_attempts = Attempt.objects.filter(quiz__creator=request.user).count()
    
    global_avg_data = Attempt.objects.filter(
        quiz__creator=request.user
    ).aggregate(Avg('score'))
    
    global_avg = global_avg_data['score__avg'] or 0

    context = {
        'quizzes': quizzes,
        'total_attempts': total_attempts, 
        'global_avg': round(global_avg, 1), 
    }
    return render(request, 'quizzes/teacher_dashboard.html', context)