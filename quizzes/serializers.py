from rest_framework import serializers
from .models import Quiz, Question, Choice, Attempt, AttemptAnswer

# --- TEACHER SERIALIZERS (Full Access & Writable) ---

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    # Removed read_only=True so we can send choices within a question
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    # Removed read_only=True so we can send questions within a quiz
    questions = QuestionSerializer(many=True)
    creator_name = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator_name', 'questions', 'created_at']

    def create(self, validated_data):
        """
        Custom logic to handle nested creation of Questions and Choices
        """
        # 1. Pull the questions data out before saving the Quiz
        questions_data = validated_data.pop('questions')
        
        # 2. Create the Quiz (creator is passed from the view's perform_create)
        quiz = Quiz.objects.create(**validated_data)
        
        # 3. Loop through each question in the list
        for question_data in questions_data:
            # Pull the choices out of the question
            choices_data = question_data.pop('choices')
            
            # Create the Question linked to our new Quiz
            question = Question.objects.create(quiz=quiz, **question_data)
            
            # 4. Loop through each choice and link it to the question
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        
        return quiz

# --- STUDENT SERIALIZERS (Read-Only & Hidden Answers) ---

class StudentChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']  # is_correct is hidden

class StudentQuestionSerializer(serializers.ModelSerializer):
    choices = StudentChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

class StudentQuizSerializer(serializers.ModelSerializer):
    questions = StudentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']


class AttemptAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = ['question', 'selected_choice']

class AttemptSerializer(serializers.ModelSerializer):
    answers = AttemptAnswerSerializer(many=True)

    class Meta:
        model = Attempt
        fields = ['id', 'quiz', 'answers', 'score', 'completed_at']
        read_only_fields = ['score', 'completed_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        quiz = validated_data['quiz']
        student = self.context['request'].user
        
        # 1. Create the initial Attempt
        attempt = Attempt.objects.create(student=student, quiz=quiz)
        
        correct_count = 0
        total_questions = quiz.questions.count()

        # 2. Process each answer and check if it's right
        for ans in answers_data:
            choice = ans['selected_choice']
            AttemptAnswer.objects.create(attempt=attempt, **ans)
            
            if choice.is_correct:
                correct_count += 1

        # 3. Calculate score (percentage)
        if total_questions > 0:
            attempt.score = (correct_count / total_questions) * 100
        
        attempt.save()
        return attempt
    
class LeaderboardSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Attempt
        fields = ['student_name', 'score', 'completed_at']