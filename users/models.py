from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ("admin", "Administrador"),
        ("professor", "Professor"),
        ("aluno", "Aluno"),
    )
    tipo = models.CharField(
        max_length=15,
        choices=TIPO_USUARIO_CHOICES,
        default="aluno",
        verbose_name="Tipo de Usuário",
    )
    profile_picture_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL da Foto de Perfil"
    )
