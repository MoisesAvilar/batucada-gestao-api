from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import (
    Modalidade,
    Aluno,
    Aula,
    PresencaAluno,
    PresencaProfessor,
    RelatorioAula,
    ItemRudimento,
    ItemRitmo,
    ItemVirada,
)
from users.models import CustomUser
from django.db.models import Count, Q, Subquery, OuterRef
from django.db.models.functions import TruncMonth
from django.utils import timezone


class ModalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidade
        fields = ['id', 'nome']


class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['id', 'nome_completo', 'telefone', 'email', 'data_criacao']


class ProfessorSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name']


class AulaSerializer(serializers.ModelSerializer):
    modalidade = ModalidadeSerializer(read_only=True)
    alunos = AlunoSerializer(many=True, read_only=True)
    professores = ProfessorSimpleSerializer(many=True, read_only=True)
    modalidade_id = serializers.PrimaryKeyRelatedField(
        queryset=Modalidade.objects.all(), source='modalidade', write_only=True
    )
    aluno_ids = serializers.PrimaryKeyRelatedField(
        queryset=Aluno.objects.all(), source='alunos', many=True, write_only=True
    )
    professor_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(tipo__in=["admin", "professor"]),
        source='professores', many=True, write_only=True
    )

    class Meta:
        model = Aula
        fields = [
            'id', 'data_hora', 'status', 'modalidade', 'alunos', 'professores',
            'modalidade_id', 'aluno_ids', 'professor_ids'
        ]


class PresencaAlunoSerializer(serializers.Serializer):
    aluno_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PresencaAluno.STATUS_CHOICES)


class PresencaProfessorSerializer(serializers.Serializer):
    professor_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PresencaProfessor.STATUS_CHOICES)


class ItemRudimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRudimento
        fields = ['id', 'descricao', 'bpm', 'duracao_min', 'observacoes']


class ItemRitmoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRitmo
        fields = ['id', 'descricao', 'livro_metodo', 'bpm', 'duracao_min', 'observacoes']


class ItemViradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVirada
        fields = ['id', 'descricao', 'bpm', 'duracao_min', 'observacoes']


class RelatorioAulaSerializer(WritableNestedModelSerializer):
    itens_rudimentos = ItemRudimentoSerializer(many=True, required=False)
    itens_ritmo = ItemRitmoSerializer(many=True, required=False)
    itens_viradas = ItemViradaSerializer(many=True, required=False)

    class Meta:
        model = RelatorioAula
        fields = [
            'aula', 'conteudo_teorico', 'observacoes_teoria', 'repertorio_musicas',
            'observacoes_repertorio', 'observacoes_gerais', 'professor_que_validou',
            'itens_rudimentos', 'itens_ritmo', 'itens_viradas'
        ]
        read_only_fields = ['professor_que_validou']


class AlunoDetailSerializer(serializers.ModelSerializer):
    """
    Um serializer detalhado para um único aluno, que calcula e anexa
    KPIs e outros dados agregados.
    """
    kpis = serializers.SerializerMethodField()
    taxa_presenca = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = [
            'id', 'nome_completo', 'telefone', 'email', 'data_criacao',
            'kpis', 'taxa_presenca'
        ]

    def _get_aulas_com_presenca_base_query(self, aluno):
        """Método auxiliar para não repetir a query base."""
        presenca_status_subquery = PresencaAluno.objects.filter(
            aula=OuterRef('pk'),
            aluno=aluno
        ).values('status')[:1]

        return Aula.objects.filter(alunos=aluno).annotate(
            status_presenca_aluno=Subquery(presenca_status_subquery)
        )

    def get_kpis(self, aluno):
        """Calcula os KPIs de aulas para o aluno."""
        aulas_com_presenca = self._get_aulas_com_presenca_base_query(aluno)

        total_realizadas = aulas_com_presenca.filter(status__in=['Realizada', 'Aluno Ausente'], status_presenca_aluno='presente').count()
        total_ausencias = aulas_com_presenca.filter(status__in=['Realizada', 'Aluno Ausente'], status_presenca_aluno='ausente').count()
        total_canceladas = aulas_com_presenca.filter(status="Cancelada").count()
        total_agendadas = aulas_com_presenca.filter(status="Agendada").count()

        return {
            'total_aulas': aulas_com_presenca.count(),
            'total_realizadas': total_realizadas,
            'total_ausencias': total_ausencias,
            'total_canceladas': total_canceladas,
            'total_agendadas': total_agendadas,
        }

    def get_taxa_presenca(self, aluno):
        """Calcula a taxa de presença do aluno."""
        kpis = self.get_kpis(aluno)
        aulas_contabilizadas = kpis['total_realizadas'] + kpis['total_ausencias']

        if aulas_contabilizadas == 0:
            return 0.0

        taxa = (kpis['total_realizadas'] / aulas_contabilizadas) * 100
        return round(taxa, 2)


class ModalidadeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para uma única modalidade, calculando KPIs
    e dados para gráficos.
    """
    kpis = serializers.SerializerMethodField()
    monthly_activity_chart = serializers.SerializerMethodField()

    class Meta:
        model = Modalidade
        fields = ['id', 'nome', 'kpis', 'monthly_activity_chart']

    def get_kpis(self, modalidade):
        """Calcula os KPIs para a modalidade."""
        aulas_da_modalidade = modalidade.aulas.all()
        now = timezone.now()

        total_aulas = aulas_da_modalidade.count()
        total_realizadas = aulas_da_modalidade.filter(status="Realizada").count()

        alunos_ativos_count = aulas_da_modalidade.filter(
            data_hora__gte=now
        ).values('alunos').distinct().count()

        professores_count = aulas_da_modalidade.filter(
            professores__isnull=False
        ).values('professores').distinct().count()

        return {
            'total_aulas': total_aulas,
            'total_realizadas': total_realizadas,
            'alunos_ativos_count': alunos_ativos_count,
            'professores_associados_count': professores_count,
        }

    def get_monthly_activity_chart(self, modalidade):
        """Gera dados para o gráfico de atividade mensal."""
        aulas_por_mes = modalidade.aulas.annotate(
            mes=TruncMonth('data_hora')
        ).values('mes').annotate(
            contagem=Count('id')
        ).order_by('mes')

        return {
            'labels': [item['mes'].strftime('%b/%Y') for item in aulas_por_mes],
            'data': [item['contagem'] for item in aulas_por_mes],
        }
