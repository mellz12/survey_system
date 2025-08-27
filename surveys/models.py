from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    title = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('active', 'Активный'), ('inactive', 'Неактивный')], default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    token = models.CharField(max_length=32, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Добавляем поле created_at

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('single_choice', 'Одиночный выбор'),
        ('multiple_choice', 'Множественный выбор'),
        ('scale', 'Шкала'),
        ('text', 'Текстовый ответ'),
    ]
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)  # Добавляем поле order

    def __str__(self):
        return self.text
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class SurveySession(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    session = models.ForeignKey(SurveySession, on_delete=models.CASCADE)
    choice_answer = models.ManyToManyField(Choice, blank=True)
    scale_answer = models.IntegerField(null=True, blank=True)
    text_answer = models.TextField(null=True, blank=True)