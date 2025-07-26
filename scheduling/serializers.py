from rest_framework import serializers
from .models import Modalidade, Aluno


class ModalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidade
        fields = ['id', 'nome']


class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['id', 'nome_completo', 'telefone', 'email', 'data_criacao']
