from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. The Landing Page is now the Login Page
    path('', auth_views.LoginView.as_view(
        template_name='login.html', 
        redirect_authenticated_user=True
    ), name='login'),

    # 2. Standard Logout (Redirects to login by default)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. Include all Quiz & API routes from the quizzes app
    path('quizzes/', include('quizzes.urls')),

    # 4. Auth API routes
    path('api/auth/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)