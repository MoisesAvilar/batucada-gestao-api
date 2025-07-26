from django.contrib import admin
from .models import (
    Modalidade,
    Aluno,
    Aula,
    RelatorioAula,
    ItemRudimento,
    ItemRitmo,
    ItemVirada,
    PresencaAluno,
    PresencaProfessor,
)

@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    """Configuração do Admin para o modelo Modalidade."""
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    """Configuração do Admin para o modelo Aluno."""
    list_display = ('nome_completo', 'email', 'telefone', 'data_criacao')
    search_fields = ('nome_completo', 'email')
    ordering = ('nome_completo',)


# Inlines para os Itens do Relatório de Aula
# Permitem editar os exercícios diretamente na página do relatório.
class ItemRudimentoInline(admin.TabularInline):
    model = ItemRudimento
    extra = 1  # Quantos formulários em branco mostrar

class ItemRitmoInline(admin.TabularInline):
    model = ItemRitmo
    extra = 1

class ItemViradaInline(admin.TabularInline):
    model = ItemVirada
    extra = 1


@admin.register(RelatorioAula)
class RelatorioAulaAdmin(admin.ModelAdmin):
    """Configuração do Admin para o Relatório de Aula, com exercícios aninhados."""
    list_display = ('aula', 'professor_que_validou', 'data_atualizacao')
    # Autocomplete para facilitar a busca de aulas e professores
    autocomplete_fields = ('aula', 'professor_que_validou')
    inlines = [
        ItemRudimentoInline,
        ItemRitmoInline,
        ItemViradaInline,
    ]


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    """
    Configuração avançada do Admin para o modelo Aula,
    com bom suporte para os campos ManyToMany.
    """
    list_display = ('data_hora', 'get_alunos_display', 'modalidade', 'get_professores_display', 'status')
    list_filter = ('status', 'modalidade', 'professores', 'data_hora')
    search_fields = ('alunos__nome_completo', 'professores__username', 'modalidade__nome')
    # Autocomplete melhora muito a usabilidade com muitos alunos/professores
    autocomplete_fields = ('alunos', 'professores')
    ordering = ('-data_hora',)
    
    # Métodos para exibir campos ManyToMany de forma legível na lista
    def get_alunos_display(self, obj):
        """Retorna os nomes dos alunos separados por vírgula."""
        return ", ".join([aluno.nome_completo for aluno in obj.alunos.all()])
    get_alunos_display.short_description = 'Alunos'

    def get_professores_display(self, obj):
        """Retorna os nomes dos professores separados por vírgula."""
        return ", ".join([prof.username for prof in obj.professores.all()])
    get_professores_display.short_description = 'Professores'


@admin.register(PresencaAluno)
class PresencaAlunoAdmin(admin.ModelAdmin):
    """Configuração do Admin para o registro de presença de alunos."""
    list_display = ('aula', 'aluno', 'status')
    list_filter = ('status',)
    autocomplete_fields = ('aula', 'aluno')


@admin.register(PresencaProfessor)
class PresencaProfessorAdmin(admin.ModelAdmin):
    """Configuração do Admin para o registro de presença de professores."""
    list_display = ('aula', 'professor', 'status')
    list_filter = ('status',)
    autocomplete_fields = ('aula', 'professor')
