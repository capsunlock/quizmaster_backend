from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Quiz, Question

# Create your tests here.

User = get_user_model()

class QuizModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher', password='password123')
        self.quiz = Quiz.objects.create(title="Math Quiz", creator=self.user)

    def test_quiz_creation(self):
        """Test if the quiz is created with the correct title"""
        self.assertEqual(self.quiz.title, "Math Quiz")
        self.assertEqual(self.quiz.creator.username, "teacher")

    def test_question_assignment(self):
        """Test if questions can be linked to a quiz"""
        question = Question.objects.create(quiz=self.quiz, text="What is 2+2?")
        self.assertEqual(self.quiz.questions.count(), 1)