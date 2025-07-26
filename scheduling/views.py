from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .filters import AulaFilter
from .models import Modalidade, Aluno, Aula, PresencaAluno, PresencaProfessor, RelatorioAula
from .serializers import ModalidadeSerializer, AlunoSerializer, AlunoDetailSerializer, AulaSerializer, PresencaAlunoSerializer, PresencaProfessorSerializer, RelatorioAulaSerializer, ModalidadeDetailSerializer


class ModalidadeViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API que permite que modalidades sejam visualizadas ou editadas.
    """
    queryset = Modalidade.objects.all().order_by('nome')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModalidadeDetailSerializer
        return ModalidadeSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API que permite que alunos sejam visualizados ou editados.
    Usa um serializer diferente para a visualização de detalhes.
    """
    queryset = Aluno.objects.all().order_by('nome_completo')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlunoDetailSerializer
        return AlunoSerializer


class AulaViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API para visualizar e agendar aulas.
    """
    queryset = Aula.objects.all().order_by('-data_hora')
    serializer_class = AulaSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_class = AulaFilter

    @action(detail=True, methods=['post'], url_path='marcar-presenca-alunos')
    def marcar_presenca_alunos(self, request, pk=None):
        """
        Ação customizada para registrar a presença de múltiplos alunos em uma aula.
        Espera uma lista de objetos: [{"aluno_id": 1, "status": "presente"}, ...]
        """
        aula = self.get_object()
        serializer = PresencaAlunoSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for item in serializer.validated_data:
            aluno_id = item['aluno_id']
            status_presenca = item['status']

            if not aula.alunos.filter(id=aluno_id).exists():
                return Response(
                    {'error': f'O aluno com ID {aluno_id} não está nesta aula.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            PresencaAluno.objects.update_or_create(
                aula=aula,
                aluno_id=aluno_id,
                defaults={'status': status_presenca}
            )

        if not PresencaAluno.objects.filter(aula=aula, status='presente').exists():
            aula.status = 'Aluno Ausente'
        else:
            aula.status = 'Realizada'
        aula.save()

        return Response({'status': 'presença atualizada com sucesso'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='marcar-presenca-professores')
    def marcar_presenca_professores(self, request, pk=None):
        """
        Ação customizada para registrar a presença de múltiplos professores em uma AC.
        Espera uma lista de objetos: [{"professor_id": 1, "status": "presente"}, ...]
        """
        aula = self.get_object()
        serializer = PresencaProfessorSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for item in serializer.validated_data:
            professor_id = item['professor_id']
            status_presenca = item['status']

            if not aula.professores.filter(id=professor_id).exists():
                return Response(
                    {'error': f'O professor com ID {professor_id} não está nesta aula.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            PresencaProfessor.objects.update_or_create(
                aula=aula,
                professor_id=professor_id,
                defaults={'status': status_presenca}
            )

        if PresencaProfessor.objects.filter(aula=aula, status='presente').exists():
            aula.status = 'Realizada'
            aula.save()

        return Response({'status': 'presença de professores atualizada com sucesso'}, status=status.HTTP_200_OK)


class RelatorioAulaViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API para criar e visualizar relatórios de aulas.
    """
    queryset = RelatorioAula.objects.all()
    serializer_class = RelatorioAulaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Define o professor que validou como o usuário logado no momento da criação.
        """
        serializer.save(professor_que_validou=self.request.user)
