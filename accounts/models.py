from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    # This identifies if the user can create quizzes (Teacher) or just take them (Student)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({'Teacher' if self.is_teacher else 'Student'})"