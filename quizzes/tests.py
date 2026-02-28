from django.test import TestCase
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