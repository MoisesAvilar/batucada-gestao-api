from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModalidadeViewSet, AlunoViewSet, AulaViewSet, RelatorioAulaViewSet


router = DefaultRouter()
router.register(r'modalidades', ModalidadeViewSet, basename='modalidade')
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'aulas', AulaViewSet, basename='aula')
router.register(r'relatorios', RelatorioAulaViewSet, basename='relatorio')

urlpatterns = [
    path('', include(router.urls)),
]
