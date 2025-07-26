from django.db import models
from django.utils import timezone


class Modalidade(models.Model):
    """
    Armazena os tipos de aulas oferecidas, como "Bateria" ou "Atividade Complementar".
    """
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    

class Aluno(models.Model):
    """
    Armazena o perfil de um aluno com seus dados de matrícula.
    Este modelo é separado da conta de usuário (CustomUser) para maior flexibilidade.
    """
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    data_criacao = models.DateField(
        default=timezone.now,
        verbose_name="Data de Criação/Matrícula"
    )

    def __str__(self):
        return self.nome_completo
