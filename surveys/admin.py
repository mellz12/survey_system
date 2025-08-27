from django.contrib import admin
from .models import Survey, Question, Choice

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_public', 'status', 'created_by', 'token', 'created_at']
    list_filter = ['is_public', 'status', 'created_by', 'created_at']
    search_fields = ['title']
    date_hierarchy = 'created_at'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'survey', 'question_type', 'is_required', 'order']
    list_filter = ['survey', 'question_type', 'is_required']
    search_fields = ['text']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question']
    list_filter = ['question']
    search_fields = ['text']