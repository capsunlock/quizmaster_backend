from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model
from quizzes.models import Attempt
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_teacher', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class RegisterSerializer(serializers.ModelSerializer):
    # Define password to make it write-only for security so it never gets sent back in a response
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_teacher')

    def create(self, validated_data):
        # We use create_user to ensure the password gets hashed (encrypted)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            is_teacher=validated_data.get('is_teacher', False)
        )
        return user
    
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    # We pull the attempts linked to this user
    total_quizzes = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    recent_attempts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'is_teacher', 'total_quizzes', 'average_score', 'recent_attempts']

    def get_total_quizzes(self, obj):
        return obj.attempts.count()

    def get_average_score(self, obj):
        # Calculate the average of all scores for this user
        avg = obj.attempts.aggregate(Avg('score'))['score__avg']
        return round(avg, 2) if avg else 0

    def get_recent_attempts(self, obj):
        # Just the last 5 attempts
        from quizzes.serializers import LeaderboardSerializer # Local import to avoid circular error
        attempts = obj.attempts.all().order_by('-completed_at')[:5]
        return LeaderboardSerializer(attempts, many=True).data