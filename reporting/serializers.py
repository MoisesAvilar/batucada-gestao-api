from rest_framework import serializers


class DashboardKpiSerializer(serializers.Serializer):
    total_aulas = serializers.IntegerField()
    total_realizadas = serializers.IntegerField()
    total_canceladas = serializers.IntegerField()
    total_aluno_ausente = serializers.IntegerField()
    taxa_sucesso_percentual = serializers.FloatField()


class ChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.IntegerField())


class ProfessorPerformanceSerializer(serializers.Serializer):
    username = serializers.CharField()
    total_realizadas = serializers.IntegerField()
    total_atribuidas = serializers.IntegerField()
    taxa_realizacao_percentual = serializers.FloatField()


class AdminDashboardSerializer(serializers.Serializer):
    """Define a estrutura completa da resposta do dashboard."""
    kpis = DashboardKpiSerializer()
    aulas_por_categoria_chart = ChartDataSerializer()
    aulas_realizadas_por_mes_chart = ChartDataSerializer()
    professor_performance = ProfessorPerformanceSerializer(many=True)
