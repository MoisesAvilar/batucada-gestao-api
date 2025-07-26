import django_filters
from .models import Aula


class AulaFilter(django_filters.FilterSet):
    """
    Define os filtros que podem ser aplicados ao endpoint de listagem de Aulas.
    """
    data_inicial = django_filters.DateFilter(field_name="data_hora__date", lookup_expr='gte')
    data_final = django_filters.DateFilter(field_name="data_hora__date", lookup_expr='lte')

    class Meta:
        model = Aula
        fields = ['status', 'modalidade', 'professores', 'alunos']
