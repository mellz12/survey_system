from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, QuestionViewSet, ChoiceViewSet, SurveySessionViewSet, ResponseViewSet, SurveyStatsView, TokenView

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'sessions', SurveySessionViewSet)
router.register(r'responses', ResponseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('surveys/<int:survey_id>/stats/', SurveyStatsView.as_view(), name='survey-stats'),
    path('token/current/', TokenView.as_view(), name='token-current'),
    
]