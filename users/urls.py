from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, ProfessorViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "users"

router = DefaultRouter()
router.register(r'professores', ProfessorViewSet, basename='professor')

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('', include(router.urls)),
]
