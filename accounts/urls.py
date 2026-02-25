from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # Login endpoint
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # For when the login expires
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]