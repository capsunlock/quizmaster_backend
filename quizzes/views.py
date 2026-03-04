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
from django.db.models import Avg, Count, Max, Min, F, Q, Subquery, OuterRef

from .models import Quiz, Attempt, AttemptAnswer, Choice, Question
from .serializers import (
    QuizSerializer, 
    StudentQuizSerializer, 
    AttemptSerializer, 
    LeaderboardSerializer
)

# --- HELPERS & PERMISSIONS ---

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_teacher

def is_teacher_check(user):
    return user.is_authenticated and user.is_teacher

# --- API VIEWS (REST Framework) ---

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

class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint to Get, Update, or Delete a specific quiz """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        # Allow teachers to edit/delete only THEIR quizzes, but anyone to view
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Quiz.objects.filter(creator=self.request.user)
        return Quiz.objects.all()

class AttemptCreateView(generics.CreateAPIView):
    """ API endpoint to create an attempt (alternative to the AJAX flow) """
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
        return Attempt.objects.filter(quiz_id=quiz_id, completed_at__isnull=False).order_by('-score', '-completed_at')[:10]

# --- TEMPLATE VIEWS (HTML Rendering) ---

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
    # START TIME TRACKING
    attempt = Attempt.objects.create(student=request.user, quiz=quiz, score=0.0)
    request.session['active_attempt_id'] = attempt.id
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})

@login_required
def leaderboard_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Subquery to get the latest score for each student
    latest_attempt = Attempt.objects.filter(
        student=OuterRef('student'),
        quiz=quiz,
        completed_at__isnull=False
    ).order_by('-completed_at')

    # Group by student and get high, low, and latest scores
    # This prevents one student from filling up the board
    leaderboard_data = Attempt.objects.filter(
        quiz=quiz, 
        completed_at__isnull=False
    ).values('student__username', 'student__id').annotate(
        best_score=Max('score'),
        worst_score=Min('score'),
        latest_score=Subquery(latest_attempt.values('score')[:1]),
        last_attempt_date=Max('completed_at')
    ).order_by('-best_score')

    return render(request, 'quizzes/leaderboard.html', {
        'quiz': quiz, 
        'leaderboard': leaderboard_data
    })

# --- DASHBOARDS ---

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return render(request, 'quizzes/403.html')

    # 1. Cleanup abandoned ghost attempts (older than 24h)
    # This removes attempts that were started but never finished
    Attempt.objects.filter(
        completed_at__isnull=True, 
        started_at__lt=timezone.now() - timedelta(hours=24)
    ).delete()

    # 2. Fetch quizzes created by this teacher and annotate with stats
    # We use Q objects to ensure we only count and average COMPLETED attempts
    quizzes = Quiz.objects.filter(creator=request.user).annotate(
        num_attempts=Count(
            'attempts', 
            filter=Q(attempts__completed_at__isnull=False)
        ),
        avg_score=Avg(
            'attempts__score', 
            filter=Q(attempts__completed_at__isnull=False)
        )
    ).order_by('-created_at')

    # 3. Calculate summary stats for the top cards
    teacher_attempts = Attempt.objects.filter(
        quiz__creator=request.user, 
        completed_at__isnull=False
    )
    
    total_attempts = teacher_attempts.count()
    global_avg = teacher_attempts.aggregate(Avg('score'))['score__avg'] or 0

    return render(request, 'quizzes/teacher_dashboard.html', {
        'quizzes': quizzes,
        'total_attempts': total_attempts, 
        'global_avg': round(global_avg, 1), 
    })

@login_required
def student_dashboard(request):
    target_user_id = request.GET.get('student_id')
    
    if target_user_id and request.user.is_teacher:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        display_user = get_object_or_404(User, id=target_user_id)
        is_owner = False
    else:
        display_user = request.user
        is_owner = True

    # 1. Define the Subquery correctly (Remove the slice from here)
    # We move the .values() and [:1] logic into the Subquery wrapper below
    latest_score_qs = Attempt.objects.filter(
        student=display_user,
        quiz_id=OuterRef('quiz_id'),
        completed_at__isnull=False
    ).order_by('-completed_at')

    # 2. Main stats query
    quiz_stats = Attempt.objects.filter(
        student=display_user, 
        completed_at__isnull=False
    ).values(
        'quiz__title', 'quiz__id'
    ).annotate(
        highest=Max('score'),
        lowest=Min('score'),
        average=Avg('score'),
        total_tries=Count('id'),
        last_date=Max('completed_at'),
        # Wrap the queryset here and apply the slice/values INSIDE the Subquery call
        latest_score=Subquery(latest_score_qs.values('score')[:1])
    ).order_by('-last_date')

    # 3. List for the bottom table
    recent_attempts_list = Attempt.objects.filter(
        student=display_user, 
        completed_at__isnull=False
    ).order_by('-completed_at')[:5]

    # 4. Global Stats
    global_stats = Attempt.objects.filter(
        student=display_user, 
        completed_at__isnull=False
    ).aggregate(
        overall_avg=Avg('score'), 
        total_count=Count('id')
    )

    return render(request, 'quizzes/student_dashboard.html', {
        'display_user': display_user,
        'is_owner': is_owner,
        'quiz_stats': quiz_stats,
        'recent_attempts_list': recent_attempts_list,
        'global_student_avg': round(global_stats['overall_avg'] or 0, 1),
        'total_attempts_count': global_stats['total_count'],
        'total_quizzes_count': quiz_stats.count(),
    })

@login_required
def quiz_history_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if teacher is looking at a specific student
    target_user_id = request.GET.get('student_id')
    
    if target_user_id and request.user.is_teacher:
        # Teacher view: Filter by the target student
        attempts = Attempt.objects.filter(student_id=target_user_id, quiz=quiz, completed_at__isnull=False)
        from django.contrib.auth import get_user_model
        student_obj = get_object_or_404(get_user_model(), id=target_user_id)
        display_name = f"{student_obj.username}'s"
    else:
        # Student view: Filter by themselves
        attempts = Attempt.objects.filter(student=request.user, quiz=quiz, completed_at__isnull=False)
        display_name = "My"

    attempts = attempts.order_by('-completed_at')
    
    return render(request, 'quizzes/quiz_history_detail.html', {
        'quiz': quiz, 
        'attempts': attempts,
        'display_name': display_name,
        'target_user_id': target_user_id # Pass this so links stay consistent
    })

# --- AJAX ENDPOINTS ---

@csrf_protect
@login_required
def api_submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quiz')
            answers_data = data.get('answers')
            
            # Use the attempt started in quiz_detail_view
            attempt_id = request.session.get('active_attempt_id')
            if not attempt_id:
                return JsonResponse({'error': 'No active attempt found. Did you refresh?'}, status=400)
                
            attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            correct_count = 0
            questions = quiz.questions.all()
            total_questions = questions.count()

            for item in answers_data:
                question = get_object_or_404(Question, id=item['question'])
                choice_id = item.get('selected_choice')
                selected_choice = None

                if choice_id:
                    selected_choice = Choice.objects.get(id=choice_id)
                    if selected_choice.is_correct:
                        correct_count += 1
                
                AttemptAnswer.objects.create(attempt=attempt, question=question, selected_choice=selected_choice)

            attempt.score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0
            attempt.completed_at = timezone.now()
            attempt.save()

            if 'active_attempt_id' in request.session:
                del request.session['active_attempt_id']

            return JsonResponse({'score': attempt.score, 'attempt_id': attempt.id})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)

@csrf_protect
@login_required
@user_passes_test(is_teacher_check)
def api_save_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz = Quiz.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                time_limit=data.get('time_limit', 30),
                creator=request.user
            )
            for q_data in data.get('questions', []):
                question = Question.objects.create(quiz=quiz, text=q_data.get('text'))
                for c_data in q_data.get('choices', []):
                    Choice.objects.create(question=question, text=c_data.get('text'), is_correct=c_data.get('is_correct', False))
            return JsonResponse({'message': 'Quiz created!', 'quiz_id': quiz.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def api_delete_quiz(request, quiz_id):
    if request.method == 'DELETE':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if quiz.creator == request.user:
            quiz.delete()
            return JsonResponse({'message': 'Deleted successfully'}, status=200)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

# --- MISC ---


@login_required
def quiz_results_view(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    if not request.user.is_teacher and attempt.student != request.user:
        raise PermissionDenied
    return render(request, 'quizzes/quiz_results.html', {'attempt': attempt})

@login_required
@user_passes_test(is_teacher_check, login_url='quiz-list')
def create_quiz_view(request):
    return render(request, 'quizzes/create_quiz.html')

@login_required
def quiz_edit_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not request.user.is_teacher or quiz.creator != request.user:
        raise PermissionDenied("Unauthorized")
    return render(request, 'quizzes/quiz_edit.html', {'quiz': quiz})

@login_required
def login_success_view(request):
    return redirect('create-quiz') if request.user.is_teacher else redirect('quiz-list')