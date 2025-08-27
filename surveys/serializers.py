from rest_framework import serializers
from .models import Survey, Question, Choice, SurveySession, Response as SurveyResponse

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order', 'choices']

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Survey
        fields = ['id', 'title', 'status', 'is_public', 'questions']

class SurveySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySession
        fields = ['id', 'survey', 'ip_address']

class ResponseSerializer(serializers.ModelSerializer):
    choice_answer = serializers.PrimaryKeyRelatedField(many=True, queryset=Choice.objects.all(), required=False)
    scale_answer = serializers.IntegerField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = SurveyResponse
        fields = ['id', 'question', 'session', 'choice_answer', 'scale_answer', 'text_answer']

    def validate(self, data):
        question = data.get('question')
        choice_answer = data.get('choice_answer', [])
        scale_answer = data.get('scale_answer')
        text_answer = data.get('text_answer')

        if question.question_type == 'single_choice' and len(choice_answer) != 1:
            raise serializers.ValidationError("Для вопроса с одним выбором должен быть ровно один ответ.")
        if question.question_type == 'multiple_choice' and not choice_answer:
            raise serializers.ValidationError("Для вопроса с множественным выбором должен быть хотя бы один ответ.")
        if question.question_type == 'scale' and scale_answer is None:
            raise serializers.ValidationError("Для вопроса типа 'scale' требуется числовой ответ.")
        if question.question_type == 'text' and not text_answer and question.is_required:
            raise serializers.ValidationError("Для вопроса типа 'text' требуется текстовый ответ, если он обязательный.")
        return data