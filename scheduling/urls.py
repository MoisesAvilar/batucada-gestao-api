from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModalidadeViewSet, AlunoViewSet, AulaViewSet


router = DefaultRouter()
router.register(r'modalidades', ModalidadeViewSet, basename='modalidade')
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'aulas', AulaViewSet, basename='aula')

urlpatterns = [
    path('', include(router.urls)),
]
