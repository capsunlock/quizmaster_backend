from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # This ensures 'is_teacher' shows up when you edit a user in Admin
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher',)}),
    )
    # Add our custom field to the 'User' list view
    list_display = ['username', 'email', 'is_teacher', 'is_staff']

admin.site.register(User, CustomUserAdmin)