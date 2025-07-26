import json
import pytest
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser
from .models import Aluno, Aula, Modalidade, PresencaAluno, PresencaProfessor, RelatorioAula, ItemRudimento


# O marcador garante que o banco de dados de teste seja usado.
@pytest.mark.django_db
def test_create_modalidade(client):
    """
    Testa se um usuário autenticado pode criar uma nova modalidade.
    """
    # Cria um usuário para o teste e faz o login para obter o token
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    
    # Faz o login para obter o token JWT
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'}, format='json')
    token = token_response.data['access']

    # URL para criar modalidades
    url = reverse('modalidade-list') # O DRF cria esse nome automaticamente: <basename>-list
    data = {'nome': 'Bateria Infantil'}

    # Faz a requisição POST com o token de autenticação
    response = client.post(
        url,
        data,
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {token}' # Envia o token
    )

    # Verificações
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['nome'] == 'Bateria Infantil'


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_modalidade(client):
    """
    Testa se um usuário não autenticado recebe um erro 401 ao tentar criar uma modalidade.
    """
    url = reverse('modalidade-list')
    data = {'nome': 'Bateria Adulto'}

    # Faz a requisição SEM o token de autenticação
    response = client.post(url, data, format='json')

    # Verifica se o acesso foi negado
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_aula(client):
    """
    Testa a criação de uma nova aula com todos os relacionamentos.
    """
    # 1. ARRANGE: Prepara todos os dados necessários para o teste
    # Cria um usuário e obtém o token
    professor_user = CustomUser.objects.create_user(username='prof1', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof1', 'password': 'password123'})
    token = token_response.data['access']

    # Cria as entidades que a Aula vai referenciar
    aluno = Aluno.objects.create(nome_completo="Aluno de Teste")
    modalidade = Modalidade.objects.create(nome="Teste de Aula")

    # URL do endpoint e dados para o POST
    url = reverse('aula-list')
    data = {
        "data_hora": "2025-08-10T15:00:00Z",
        "status": "Agendada",
        "modalidade_id": modalidade.id,
        "aluno_ids": [aluno.id],
        "professor_ids": [professor_user.id]
    }

    # 2. ACT: Faz a requisição autenticada
    response = client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')

    # 3. ASSERT: Verifica os resultados
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == 'Agendada'

    # Verifica se os detalhes aninhados estão na resposta de leitura
    assert response.data['modalidade']['nome'] == 'Teste de Aula'
    assert response.data['alunos'][0]['nome_completo'] == 'Aluno de Teste'
    assert response.data['professores'][0]['username'] == 'prof1'


@pytest.mark.django_db
def test_marcar_presenca_alunos_em_aula(client):
    """
    Testa a ação customizada de marcar a presença dos alunos em uma aula.
    """
    # 1. PREPARAÇÃO (Arrange)
    # Cria um professor para autenticar a requisição
    professor = CustomUser.objects.create_user(username='prof_presenca', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof_presenca', 'password': 'password123'})
    token = token_response.data['access']
    aluno1 = Aluno.objects.create(nome_completo="Aluno Presente")
    aluno2 = Aluno.objects.create(nome_completo="Aluno Ausente")
    modalidade = Modalidade.objects.create(nome="Aula de Presença")
    aula = Aula.objects.create(modalidade=modalidade, data_hora="2025-08-11T10:00:00Z")
    aula.alunos.set([aluno1, aluno2])
    aula.professores.set([professor])
    url = reverse('aula-marcar-presenca-alunos', kwargs={'pk': aula.pk})
    payload = [
        {"aluno_id": aluno1.id, "status": "presente"},
        {"aluno_id": aluno2.id, "status": "ausente"}
    ]

    # 2. AÇÃO (Act) - LINHA CORRIGIDA
    response = client.post(
        url,
        json.dumps(payload),  # Converte a lista para uma string JSON
        content_type='application/json',  # Informa o tipo do conteúdo
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    # 3. VERIFICAÇÃO (Assert)
    assert response.status_code == status.HTTP_200_OK
    assert PresencaAluno.objects.count() == 2
    assert PresencaAluno.objects.get(aluno=aluno1).status == 'presente'
    assert PresencaAluno.objects.get(aluno=aluno2).status == 'ausente'
    aula.refresh_from_db()
    assert aula.status == 'Realizada'


@pytest.mark.django_db
def test_marcar_presenca_professores_em_ac(client):
    """
    Testa a ação customizada de marcar a presença dos professores em uma Atividade Complementar.
    """
    # 1. PREPARAÇÃO (Arrange)
    admin_user = CustomUser.objects.create_user(username='admin_user', password='password123', tipo='admin')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'admin_user', 'password': 'password123'})
    token = token_response.data['access']
    prof1 = CustomUser.objects.create_user(username='prof_presente', password='password123', tipo='professor')
    prof2 = CustomUser.objects.create_user(username='prof_ausente', password='password123', tipo='professor')
    modalidade_ac = Modalidade.objects.create(nome="Atividade Complementar")
    aula_ac = Aula.objects.create(modalidade=modalidade_ac, data_hora="2025-08-12T14:00:00Z")
    aula_ac.professores.set([prof1, prof2])
    url = reverse('aula-marcar-presenca-professores', kwargs={'pk': aula_ac.pk})
    payload = [
        {"professor_id": prof1.id, "status": "presente"},
        {"professor_id": prof2.id, "status": "ausente"}
    ]

    # 2. AÇÃO (Act) - LINHA CORRIGIDA
    response = client.post(
        url,
        json.dumps(payload),  # Converte a lista para uma string JSON
        content_type='application/json',  # Informa o tipo do conteúdo
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    # 3. VERIFICAÇÃO (Assert)
    assert response.status_code == status.HTTP_200_OK
    assert PresencaProfessor.objects.count() == 2
    assert PresencaProfessor.objects.get(professor=prof1).status == 'presente'
    aula_ac.refresh_from_db()
    assert aula_ac.status == 'Realizada'


@pytest.mark.django_db
def test_create_relatorio_with_nested_items(client):
    """
    Testa a criação de um RelatorioAula com itens aninhados (rudimentos, etc.).
    """
    # 1. PREPARAÇÃO
    # Cria um professor, uma modalidade, um aluno e uma aula
    professor = CustomUser.objects.create_user(username='prof_relatorio', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof_relatorio', 'password': 'password123'})
    token = token_response.data['access']
    modalidade = Modalidade.objects.create(nome="Aula com Relatório")
    aluno = Aluno.objects.create(nome_completo="Aluno para Relatório")
    aula = Aula.objects.create(modalidade=modalidade, data_hora="2025-08-20T10:00:00Z")
    aula.alunos.set([aluno])
    aula.professores.set([professor])
    url = reverse('relatorio-list')
    payload = {
        "aula": aula.pk,
        "conteudo_teorico": "Escalas Maiores",
        "itens_rudimentos": [{"descricao": "Toque Simples", "bpm": "120", "observacoes": "Manter consistência"}],
        "itens_ritmo": [{"descricao": "Groove de Rock Básico", "livro_metodo": "Página 10", "bpm": "100"}],
        "itens_viradas": []
    }
    
    # --- AÇÃO (Act) - LINHA CORRIGIDA ---
    # Usamos json.dumps e content_type, removendo format='json'
    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    # --- VERIFICAÇÃO (Assert) ---
    assert response.status_code == status.HTTP_201_CREATED
    assert RelatorioAula.objects.count() == 1
    relatorio = RelatorioAula.objects.first()
    assert relatorio.professor_que_validou == professor
    assert relatorio.itens_rudimentos.count() == 1
    assert relatorio.itens_ritmo.count() == 1
    assert relatorio.itens_viradas.count() == 0
    assert relatorio.itens_rudimentos.first().descricao == "Toque Simples"


@pytest.mark.django_db
def test_aluno_detail_endpoint_returns_kpis(client):
    """
    Testa se o endpoint de detalhe do aluno retorna os KPIs calculados corretamente.
    """
    # 1. ARRANGE
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'})
    token = token_response.data['access']
    
    aluno = Aluno.objects.create(nome_completo="Aluno KPI")
    modalidade = Modalidade.objects.create(nome="Aula KPI")

    # Cria um cenário de aulas e presenças
    # Aula 1: Presente
    aula1 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-01T10:00:00Z", status="Realizada")
    aula1.alunos.set([aluno])
    PresencaAluno.objects.create(aula=aula1, aluno=aluno, status='presente')

    # Aula 2: Presente
    aula2 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-02T10:00:00Z", status="Realizada")
    aula2.alunos.set([aluno])
    PresencaAluno.objects.create(aula=aula2, aluno=aluno, status='presente')

    # Aula 3: Ausente
    aula3 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-03T10:00:00Z", status="Aluno Ausente")
    aula3.alunos.set([aluno])
    PresencaAluno.objects.create(aula=aula3, aluno=aluno, status='ausente')
    
    # Aula 4: Cancelada (não conta para presença)
    aula4 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-04T10:00:00Z", status="Cancelada")
    aula4.alunos.set([aluno])
    
    # Aula 5: Agendada
    aula5 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-05T10:00:00Z", status="Agendada")
    aula5.alunos.set([aluno])
    
    # 2. ACT
    url = reverse('aluno-detail', kwargs={'pk': aluno.pk})
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    # 3. ASSERT
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica os KPIs
    kpis = response.data['kpis']
    assert kpis['total_aulas'] == 5
    assert kpis['total_realizadas'] == 2 # Apenas as com status 'presente'
    assert kpis['total_ausencias'] == 1
    assert kpis['total_canceladas'] == 1
    assert kpis['total_agendadas'] == 1
    
    # Verifica a taxa de presença (2 presentes de 3 aulas concluídas [2p + 1a])
    assert response.data['taxa_presenca'] == 66.67 
