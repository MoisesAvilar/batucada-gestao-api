from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModalidadeViewSet, AlunoViewSet


router = DefaultRouter()
router.register(r'modalidades', ModalidadeViewSet, basename='modalidade')
router.register(r'alunos', AlunoViewSet, basename='aluno')

urlpatterns = [
    path('', include(router.urls)),
]
