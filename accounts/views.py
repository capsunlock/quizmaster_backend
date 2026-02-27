from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from .serializers import RegisterSerializer, UserProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Create your views here.

class RegisterView(generics.CreateAPIView):

    # Anyone can access this view (you don't have to be logged in to sign up)

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "User": {
                    "username": user.username,
                    "email": user.email,
                    "is_teacher": user.is_teacher
                },
                "message": "Registration successful"
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom data to the response
        data['is_teacher'] = self.user.is_teacher
        
        # Logic: If NOT a teacher, tell them to go to quizzes
        if not self.user.is_teacher:
            data['next_url'] = '/api/quizzes/'
        else:
            data['next_url'] = '/admin/' # Teachers might go to admin
            
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # This returns the profile of the person currently logged in
        return self.request.user