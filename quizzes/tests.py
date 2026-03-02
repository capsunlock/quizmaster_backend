from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Quiz, Question
from django.urls import reverse
import json

# Create your tests here.

User = get_user_model()

class QuizModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher', password='password123')
        self.quiz = Quiz.objects.create(title="Math Quiz", creator=self.user)

    def test_quiz_creation(self):
        # Test if the quiz is created with the correct title
        self.assertEqual(self.quiz.title, "Math Quiz")
        self.assertEqual(self.quiz.creator.username, "teacher")

    def test_question_assignment(self):
        # Test if questions can be linked to a quiz
        question = Question.objects.create(quiz=self.quiz, text="What is 2+2?")
        self.assertEqual(self.quiz.questions.count(), 1)
    
class QuizAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        self.client.login(username='student', password='password123')
        self.quiz = Quiz.objects.create(title="Science Quiz", creator=self.user)

    def test_api_submission(self):
        # Test that a student can submit a quiz via the API
        url = reverse('api-quiz-submit')
        data = {
            "quiz": self.quiz.id,
            "answers": []  # Empty answers for a quick test
        }
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        # Check if the submission worked
        self.assertIn(response.status_code, [200, 201])
        self.assertIn('attempt_id', response.json())

class QuizPermissionsTest(TestCase):
    def setUp(self):
        # 1. Create a Teacher
        self.teacher = User.objects.create_user(username='teacher1', password='pass', is_teacher=True)
        # 2. Create another Teacher (The "Intruder")
        self.other_teacher = User.objects.create_user(username='teacher2', password='pass', is_teacher=True)
        # 3. Create a Student
        self.student = User.objects.create_user(username='student1', password='pass', is_teacher=False)
        
        # 4. Create a Quiz owned by teacher1
        from .models import Quiz
        self.quiz = Quiz.objects.create(
            title="Marvel Quiz", 
            description="Test Desc", 
            creator=self.teacher
        )
        
        self.client = Client()

    def test_student_cannot_edit_quiz(self):
        """Verify that a student gets a 403 or redirect when trying to edit"""
        self.client.login(username='student1', password='pass')
        response = self.client.get(reverse('quiz-edit', args=[self.quiz.id]))
        # It should raise PermissionDenied (403)
        self.assertEqual(response.status_code, 403)

    def test_other_teacher_cannot_edit_quiz(self):
        """Verify teacher2 cannot edit teacher1's quiz"""
        self.client.login(username='teacher2', password='pass')
        response = self.client.get(reverse('quiz-edit', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)

    def test_creator_can_access_edit_page(self):
        """Verify the actual owner can see the edit page"""
        self.client.login(username='teacher1', password='pass')
        response = self.client.get(reverse('quiz-edit', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Quiz")

    def test_api_patch_updates_title(self):
        """Verify the AJAX PATCH request actually changes the database"""
        self.client.login(username='teacher1', password='pass')
        url = reverse('api-quiz-detail', args=[self.quiz.id])
        data = {'title': 'Updated Marvel Quiz'}
        
        # Sending a PATCH request via the API
        response = self.client.patch(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Updated Marvel Quiz')