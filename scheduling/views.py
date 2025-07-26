from rest_framework import viewsets, permissions
from .models import Modalidade, Aluno
from .serializers import ModalidadeSerializer, AlunoSerializer


class ModalidadeViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API que permite que modalidades sejam visualizadas ou editadas.
    """
    queryset = Modalidade.objects.all().order_by('nome')
    serializer_class = ModalidadeSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlunoViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API que permite que alunos sejam visualizados ou editados.
    """
    queryset = Aluno.objects.all().order_by('nome_completo')
    serializer_class = AlunoSerializer
    permission_classes = [permissions.IsAuthenticated]
