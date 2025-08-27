from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from surveys.views import home, profile_view, public_surveys, survey_detail, register, survey_create, survey_edit

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('surveys.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/current/', TokenObtainPairView.as_view(), name='token_current'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('', home, name='home'),
    path('profile/', profile_view, name='profile'),
    path('public-surveys/', public_surveys, name='public_surveys'),
    path('survey/create/', survey_create, name='survey_create'),  # Добавляем маршрут для создания
    path('survey/<int:survey_id>/edit/', survey_edit, name='survey_edit'),
    path('survey/<str:token>/', survey_detail, name='survey_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)