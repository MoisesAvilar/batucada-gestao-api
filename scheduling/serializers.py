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
