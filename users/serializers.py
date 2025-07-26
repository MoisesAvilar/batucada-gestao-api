from rest_framework import serializers
from django.db.models import Count, Q
from .models import CustomUser
from scheduling.models import Aula, PresencaProfessor
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


class ProfessorDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para um único professor, calculando seus KPIs de performance.
    """
    kpis = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'tipo',
            'profile_picture_url', 'kpis'
        ]

    def get_kpis(self, professor):
        """
        Calcula os KPIs de performance baseados nas aulas do professor.
        Lê os filtros de data a partir dos parâmetros da URL.
        """
        request = self.context.get('request')
        data_inicial_str = request.query_params.get('data_inicial')
        data_final_str = request.query_params.get('data_final')

        aulas_relacionadas = Aula.objects.filter(
            Q(professores=professor) | Q(relatorio__professor_que_validou=professor)
        ).distinct()

        # Aplica filtros de data, se existirem
        if data_inicial_str:
            aulas_relacionadas = aulas_relacionadas.filter(data_hora__date__gte=data_inicial_str)
        if data_final_str:
            aulas_relacionadas = aulas_relacionadas.filter(data_hora__date__lte=data_final_str)

        # Contagem de aulas normais que ele validou
        realizadas_normal = aulas_relacionadas.filter(
            status__in=['Realizada', 'Aluno Ausente'],
            relatorio__professor_que_validou=professor
        ).exclude(modalidade__nome__icontains="atividade complementar").count()

        realizadas_ac = aulas_relacionadas.filter(
            status='Realizada',
            modalidade__nome__icontains="atividade complementar",
            presencas_professores__professor=professor,
            presencas_professores__status='presente'
        ).count()
        
        # Lógica de substituição
        total_substituicoes_feitas = aulas_relacionadas.filter(
            status='Realizada', relatorio__professor_que_validou=professor
        ).exclude(professores=professor).count()

        total_substituicoes_sofridas = aulas_relacionadas.filter(
            status='Realizada', professores=professor
        ).exclude(relatorio__professor_que_validou=professor).count()

        return {
            'total_realizadas': realizadas_normal + realizadas_ac,
            'total_agendadas': aulas_relacionadas.filter(status='Agendada', professores=professor).count(),
            'total_canceladas': aulas_relacionadas.filter(status='Cancelada', professores=professor).count(),
            'total_substituicoes_feitas': total_substituicoes_feitas,
            'total_substituicoes_sofridas': total_substituicoes_sofridas,
        }