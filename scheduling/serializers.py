from rest_framework import serializers
from .models import Modalidade, Aluno, Aula, PresencaAluno, PresencaProfessor
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
            'id', 'data_hora', 'status',
            'modalidade', 'alunos', 'professores',
            'modalidade_id', 'aluno_ids', 'professor_ids'
        ]


class PresencaAlunoSerializer(serializers.Serializer):
    aluno_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PresencaAluno.STATUS_CHOICES)


class PresencaProfessorSerializer(serializers.Serializer):
    professor_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PresencaProfessor.STATUS_CHOICES)
