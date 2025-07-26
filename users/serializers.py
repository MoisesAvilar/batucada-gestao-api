from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para o registro de novos usuários. Garante que as senhas
    sejam validadas e que o usuário seja criado corretamente.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        label="Confirme a senha",
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """
        Valida se as duas senhas fornecidas são iguais.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})

        return attrs

    def create(self, validated_data):
        """
        Cria e retorna um novo usuário usando o método `create_user` do Django,
        que lida corretamente com a hash da senha.
        """
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para ler os dados de um usuário. Usado para retornar informações
    do usuário de forma segura, sem expor a senha.
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'tipo', 'profile_picture_url')
