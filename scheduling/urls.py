from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AulasParaSubstituirAPIView, ModalidadeViewSet, AlunoViewSet, AulaViewSet, RelatorioAulaViewSet

app_name = "scheduling"

router = DefaultRouter()
router.register(r'modalidades', ModalidadeViewSet, basename='modalidade')
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'aulas', AulaViewSet, basename='aula')
router.register(r'relatorios', RelatorioAulaViewSet, basename='relatorio')

urlpatterns = [
    path("aulas/substituicao/", AulasParaSubstituirAPIView.as_view(), name="aulas-substituicao"),
    path('', include(router.urls)),
]
