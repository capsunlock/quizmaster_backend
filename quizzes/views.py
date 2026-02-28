import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone 
from datetime import timedelta    
from .models import Quiz, Attempt, AttemptAnswer, Choice, Question
from .serializers import (
    QuizSerializer, 
    StudentQuizSerializer, 
    AttemptSerializer, 
    LeaderboardSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

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
    quizzes = Quiz.objects.all().order_by('-created_at')
    recent_cutoff = timezone.now() - timedelta(hours=24)
    
    return render(request, 'quiz_list.html', { 
        'quizzes': quizzes,
        'recent_cutoff': recent_cutoff
    })

def quiz_detail_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quiz_detail.html', {'quiz': quiz})


def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # We use prefetch_related to get all questions and choices in one go (faster)
    questions = quiz.questions.all().prefetch_related('choices')
    
    if request.method == 'POST':
        # Create the Attempt
        attempt = Attempt.objects.create(student=request.user, quiz=quiz)
        correct_count = 0
        total_questions = questions.count()

        # Loop through questions to process answers
        for question in questions:
            # The 'name' in our HTML radio buttons will be 'question_<id>'
            choice_id = request.POST.get(f'question_{question.id}')
            
            if choice_id:
                selected_choice = get_object_or_404(Choice, id=choice_id)
                
                # Save the individual answer
                AttemptAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice
                )
                
                # Check if it was correct
                if selected_choice.is_correct:
                    correct_count += 1

        # Calculate and save the final score
        if total_questions > 0:
            attempt.score = (correct_count / total_questions) * 100
            attempt.save()

        return redirect('quiz_results', attempt_id=attempt.id)

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
def login_success_view(request):
    
    """
    Redirects users based on their role after a successful login.
    """
    if request.user.is_teacher:
        return redirect('create-quiz')
    else:
        return redirect('quiz-list')
    
def quiz_results_view(request, attempt_id):
    # Fetch the specific attempt, ensuring it belongs to the logged-in student
    attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
    
    return render(request, 'quizzes/quiz_results.html', {
        'attempt': attempt
    })
    
@csrf_protect
def api_submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quiz')
            answers_data = data.get('answers')
            
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            # 1. Create the Attempt record
            attempt = Attempt.objects.create(
                student=request.user,
                quiz=quiz
            )
            
            correct_count = 0
            questions = quiz.questions.all()
            total_questions = questions.count()

            # 2. Save each answer and track score
            for item in answers_data:
                question = get_object_or_404(Question, id=item['question'])
                selected_choice = get_object_or_404(Choice, id=item['selected_choice'])
                
                AttemptAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice
                )
                
                if selected_choice.is_correct:
                    correct_count += 1

            # 3. Finalize score
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            attempt.score = round(score, 2) # Rounding to 2 decimal places looks better
            attempt.save()

            return JsonResponse({
                'score': attempt.score,
                'attempt_id': attempt.id
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"DEBUG ERROR: {e}")
            return JsonResponse({'error': str(e)}, status=400)

@user_passes_test(is_teacher_check, login_url='quiz-list', redirect_field_name=None)
def create_quiz_view(request):
    return render(request, 'create_quiz.html')

def leaderboard_view(request):
    attempts = Attempt.objects.select_related('student').order_by('-score')[:10]
    return render(request, 'leaderboard.html', {'attempts': attempts})

def result_view(request):
    return render(request, 'quizzes/quiz_results.html')