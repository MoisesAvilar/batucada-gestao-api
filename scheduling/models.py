from django.conf import settings
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


class Aula(models.Model):
    STATUS_AULA_CHOICES = (
        ("Agendada", "Agendada"),
        ("Realizada", "Realizada"),
        ("Cancelada", "Cancelada"),
        ("Aluno Ausente", "Aluno Ausente"),
    )

    alunos = models.ManyToManyField(
        "Aluno",
        blank=True,
        related_name="aulas"
    )

    professores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={"tipo__in": ["admin", "professor"]},
        related_name="aulas"
    )

    modalidade = models.ForeignKey(
        Modalidade,
        on_delete=models.PROTECT,
        related_name="aulas"
    )
    data_hora = models.DateTimeField(verbose_name="Data e Horário")
    status = models.CharField(
        max_length=20, choices=STATUS_AULA_CHOICES, default="Agendada"
    )

    def __str__(self):
        nomes_alunos = ", ".join([aluno.nome_completo for aluno in self.alunos.all()])
        return f"{self.modalidade.nome} com {nomes_alunos or 'ninguém'} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class PresencaAluno(models.Model):
    STATUS_CHOICES = (
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    )
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="presencas_alunos")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="presencas")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='presente')

    class Meta:
        unique_together = ('aula', 'aluno')

    def __str__(self):
        return f"{self.aluno.nome_completo} - {self.get_status_display()} em {self.aula}"


class PresencaProfessor(models.Model):
    STATUS_CHOICES = (
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    )
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="presencas_professores")
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='presencas_registradas'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='presente')

    class Meta:
        unique_together = ('aula', 'professor')

    def __str__(self):
        return f"{self.professor.username} - {self.get_status_display()} em {self.aula}"
