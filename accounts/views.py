from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from .serializers import RegisterSerializer


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