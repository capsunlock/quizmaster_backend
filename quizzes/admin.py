from django.contrib import admin
from .models import Quiz, Question, Choice, Attempt, AttemptAnswer

# Register your models here.

# This makes it easier to add choices while looking at the question
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4 # Shows 4 blank slots by default

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Attempt)
admin.site.register(AttemptAnswer)