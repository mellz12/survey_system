from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count, Avg
from .models import Survey, Question, Choice, Response as SurveyResponse, SurveySession
from .serializers import SurveySerializer, QuestionSerializer, ChoiceSerializer, ResponseSerializer, SurveySessionSerializer
from .forms import SurveyForm, QuestionFormSet, ChoiceFormSet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import uuid

def home(request):
    surveys = Survey.objects.filter(created_by=request.user) if request.user.is_authenticated else Survey.objects.none()
    public_surveys = Survey.objects.filter(is_public=True, status='active')
    return render(request, 'home.html', {
        'surveys': surveys,
        'public_surveys': public_surveys
    })

@login_required
def survey_create(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        print("POST data:", request.POST)
        print("Form valid:", form.is_valid())
        print("Form errors:", form.errors)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.token = str(uuid.uuid4()).replace('-', '')
            survey.save()
            print("Saved survey:", survey.id)
            question_formset = QuestionFormSet(request.POST, prefix='questions')
            print("Question formset valid:", question_formset.is_valid())
            print("Question formset errors:", question_formset.errors)
            if question_formset.is_valid():
                for question_index, question_form in enumerate(question_formset):
                    if question_form.cleaned_data:
                        question = question_form.save(commit=False)
                        question.survey = survey
                        question.save()
                        print(f"Saved question {question_index}: {question.id} - {question.text}")
                        if question.question_type in ['single_choice', 'multiple_choice']:
                            choice_formset = ChoiceFormSet(request.POST, prefix=f'choices-{question_index}')
                            print(f"Choice formset for question {question_index} valid:", choice_formset.is_valid())
                            print(f"Choice formset errors for question {question_index}:", choice_formset.errors)
                            print(f"Choice formset data for question {question_index}:", request.POST.getlist(f'choices-{question_index}-text'))
                            if choice_formset.is_valid():
                                for choice_form in choice_formset:
                                    if choice_form.cleaned_data:
                                        choice = choice_form.save(commit=False)
                                        choice.question = question
                                        choice.save()
                                        print(f"Saved choice for question {question_index}: {choice.id} - {choice.text}")
            return redirect('profile')
    else:
        form = SurveyForm()
        question_formset = QuestionFormSet(prefix='questions')
        choice_formsets = [ChoiceFormSet(prefix=f'choices-{i}') for i in range(question_formset.total_form_count())]
    return render(request, 'survey_create.html', {
        'form': form,
        'question_formset': question_formset,
        'choice_formsets': choice_formsets
    })

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def survey_edit(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, created_by=request.user)
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = SurveyForm(instance=survey)
    return render(request, 'survey_edit.html', {'form': form, 'survey': survey})

def survey_detail(request, token):
    survey = get_object_or_404(Survey, token=token)
    if not (survey.is_public and survey.status == 'active'):
        if not (request.user.is_authenticated and request.user == survey.created_by):
            return render(request, 'survey_detail.html', {
                'survey': survey,
                'error': 'Этот опрос недоступен. Только создатель может просматривать непубличные или неактивные опросы.'
            })
    return render(request, 'survey_detail.html', {'survey': survey})

class SurveyDetail(APIView):
    def get(self, request, token):
        survey = get_object_or_404(Survey, token=token)
        if not (survey.is_public and survey.status == 'active'):
            if not (request.user.is_authenticated and request.user == survey.created_by):
                return Response({'error': 'This survey is not accessible.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SurveySerializer(survey)
        return Response(serializer.data)

def public_surveys(request):
    surveys = Survey.objects.filter(is_public=True, status='active')
    return render(request, 'public_surveys.html', {'surveys': surveys})

class TokenView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Survey.objects.filter(created_by=self.request.user)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Question.objects.filter(survey__created_by=self.request.user)

class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Choice.objects.filter(question__survey__created_by=self.request.user)

class SurveySessionViewSet(viewsets.ModelViewSet):
    queryset = SurveySession.objects.all()
    serializer_class = SurveySessionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return SurveySession.objects.filter(survey__created_by=self.request.user)
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

class ResponseViewSet(viewsets.ModelViewSet):
    queryset = SurveyResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return SurveyResponse.objects.filter(question__survey__created_by=self.request.user)
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

class SurveyStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, survey_id):
        try:
            survey = Survey.objects.get(id=survey_id, created_by=request.user)
        except Survey.DoesNotExist:
            return Response({"error": "Опрос не найден или вы не автор"}, status=status.HTTP_404_NOT_FOUND)
        stats = []
        for question in survey.questions.all():
            question_stats = {"question_id": question.id, "text": question.text, "type": question.question_type, "answers": []}
            if question.question_type in ["single_choice", "multiple_choice"]:
                choices = question.choices.all()
                for choice in choices:
                    count = SurveyResponse.objects.filter(question=question, choice_answer=choice).count()
                    question_stats["answers"].append({"choice_id": choice.id, "text": choice.text, "count": count})
            elif question.question_type == "scale":
                avg = SurveyResponse.objects.filter(question=question).aggregate(avg=Avg('scale_answer'))['avg']
                question_stats["answers"].append({"average": avg or 0})
            elif question.question_type == "text":
                text_answers = SurveyResponse.objects.filter(question=question).values_list('text_answer', flat=True)[:5]
                question_stats["answers"] = list(text_answers)
            stats.append(question_stats)
        return Response(stats)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})