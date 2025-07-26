import json
import pytest
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from users.models import CustomUser
from .models import Aluno, Aula, Modalidade, PresencaAluno, PresencaProfessor, RelatorioAula, ItemRudimento
from unittest.mock import patch

@pytest.mark.django_db
def test_create_modalidade(client):
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'}, format='json')
    token = token_response.data['access']
    url = reverse('scheduling:modalidade-list') # CORRIGIDO
    data = {'nome': 'Bateria Infantil'}
    response = client.post(
        url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['nome'] == 'Bateria Infantil'


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_modalidade(client):
    url = reverse('scheduling:modalidade-list') # CORRIGIDO
    data = {'nome': 'Bateria Adulto'}
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_aula(client):
    professor_user = CustomUser.objects.create_user(username='prof1', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof1', 'password': 'password123'})
    token = token_response.data['access']
    aluno = Aluno.objects.create(nome_completo="Aluno de Teste")
    modalidade = Modalidade.objects.create(nome="Teste de Aula")
    url = reverse('scheduling:aula-list') # CORRIGIDO
    data = {
        "data_hora": "2025-08-10T15:00:00Z", "status": "Agendada",
        "modalidade_id": modalidade.id, "aluno_ids": [aluno.id],
        "professor_ids": [professor_user.id]
    }
    response = client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['modalidade']['nome'] == 'Teste de Aula'
    assert response.data['alunos'][0]['nome_completo'] == 'Aluno de Teste'


@pytest.mark.django_db
def test_marcar_presenca_alunos_em_aula(client):
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
    url = reverse('scheduling:aula-marcar-presenca-alunos', kwargs={'pk': aula.pk}) # CORRIGIDO
    payload = [{"aluno_id": aluno1.id, "status": "presente"}, {"aluno_id": aluno2.id, "status": "ausente"}]
    response = client.post(
        url, json.dumps(payload), content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert PresencaAluno.objects.count() == 2
    aula.refresh_from_db()
    assert aula.status == 'Realizada'


@pytest.mark.django_db
def test_marcar_presenca_professores_em_ac(client):
    admin_user = CustomUser.objects.create_user(username='admin_user', password='password123', tipo='admin')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'admin_user', 'password': 'password123'})
    token = token_response.data['access']
    prof1 = CustomUser.objects.create_user(username='prof_presente', tipo='professor')
    prof2 = CustomUser.objects.create_user(username='prof_ausente', tipo='professor')
    modalidade_ac = Modalidade.objects.create(nome="Atividade Complementar")
    aula_ac = Aula.objects.create(modalidade=modalidade_ac, data_hora="2025-08-12T14:00:00Z")
    aula_ac.professores.set([prof1, prof2])
    url = reverse('scheduling:aula-marcar-presenca-professores', kwargs={'pk': aula_ac.pk}) # CORRIGIDO
    payload = [{"professor_id": prof1.id, "status": "presente"}, {"professor_id": prof2.id, "status": "ausente"}]
    response = client.post(
        url, json.dumps(payload), content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert PresencaProfessor.objects.count() == 2
    aula_ac.refresh_from_db()
    assert aula_ac.status == 'Realizada'


@pytest.mark.django_db
def test_create_relatorio_with_nested_items(client):
    professor = CustomUser.objects.create_user(username='prof_relatorio', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof_relatorio', 'password': 'password123'})
    token = token_response.data['access']
    modalidade = Modalidade.objects.create(nome="Aula com Relatório")
    aluno = Aluno.objects.create(nome_completo="Aluno para Relatório")
    aula = Aula.objects.create(modalidade=modalidade, data_hora="2025-08-20T10:00:00Z")
    aula.alunos.set([aluno])
    aula.professores.set([professor])
    url = reverse('scheduling:relatorio-list') # CORRIGIDO
    payload = {
        "aula": aula.pk, "conteudo_teorico": "Escalas Maiores",
        "itens_rudimentos": [{"descricao": "Toque Simples", "bpm": "120"}],
        "itens_ritmo": [{"descricao": "Groove de Rock", "bpm": "100"}],
        "itens_viradas": []
    }
    response = client.post(
        url, data=json.dumps(payload), content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert RelatorioAula.objects.count() == 1
    relatorio = RelatorioAula.objects.first()
    assert relatorio.professor_que_validou == professor
    assert relatorio.itens_rudimentos.count() == 1


@pytest.mark.django_db
def test_aluno_detail_endpoint_returns_kpis(client):
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'})
    token = token_response.data['access']
    aluno = Aluno.objects.create(nome_completo="Aluno KPI")
    modalidade = Modalidade.objects.create(nome="Aula KPI")
    aula1 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-01T10:00:00Z", status="Realizada")
    aula1.alunos.set([aluno]); PresencaAluno.objects.create(aula=aula1, aluno=aluno, status='presente')
    aula2 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-02T10:00:00Z", status="Realizada")
    aula2.alunos.set([aluno]); PresencaAluno.objects.create(aula=aula2, aluno=aluno, status='presente')
    aula3 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-03T10:00:00Z", status="Aluno Ausente")
    aula3.alunos.set([aluno]); PresencaAluno.objects.create(aula=aula3, aluno=aluno, status='ausente')
    aula4 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-04T10:00:00Z", status="Cancelada")
    aula4.alunos.set([aluno])
    aula5 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-05T10:00:00Z", status="Agendada")
    aula5.alunos.set([aluno])
    url = reverse('scheduling:aluno-detail', kwargs={'pk': aluno.pk}) # CORRIGIDO
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_200_OK
    kpis = response.data['kpis']
    assert kpis['total_aulas'] == 5
    assert kpis['total_realizadas'] == 2
    assert response.data['taxa_presenca'] == 66.67


@pytest.mark.django_db
def test_modalidade_detail_endpoint_returns_kpis(client):
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'})
    token = token_response.data['access']
    modalidade = Modalidade.objects.create(nome="Bateria Avançado")
    aluno1 = Aluno.objects.create(nome_completo="Aluno Ativo 1")
    prof1 = CustomUser.objects.create_user(username='prof1', tipo='professor')
    Aula.objects.create(modalidade=modalidade, data_hora="2025-01-01T10:00:00Z", status="Realizada")
    aula_futura = Aula.objects.create(modalidade=modalidade, data_hora="2026-01-01T10:00:00Z", status="Agendada")
    aula_futura.alunos.set([aluno1]); aula_futura.professores.set([prof1])
    url = reverse('scheduling:modalidade-detail', kwargs={'pk': modalidade.pk}) # CORRIGIDO
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_200_OK
    kpis = response.data['kpis']
    assert kpis['total_aulas'] == 2
    assert kpis['alunos_ativos_count'] == 1


@pytest.mark.django_db
def test_aula_list_endpoint_can_be_filtered(client):
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'})
    token = token_response.data['access']
    prof1 = CustomUser.objects.create_user(username='prof1', tipo='professor')
    modalidade1 = Modalidade.objects.create(nome="Modalidade A")
    modalidade2 = Modalidade.objects.create(nome="Modalidade B")
    Aula.objects.create(modalidade=modalidade1, data_hora="2025-10-10T10:00:00Z", status="Agendada")
    Aula.objects.create(modalidade=modalidade1, data_hora="2025-10-11T12:00:00Z", status="Realizada")
    aula_cancelada = Aula.objects.create(modalidade=modalidade2, data_hora="2025-10-12T14:00:00Z", status="Cancelada")
    aula_cancelada.professores.set([prof1])
    url = reverse('scheduling:aula-list') # CORRIGIDO
    response = client.get(f"{url}?status=Cancelada", HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    response = client.get(f"{url}?data_inicial=2025-10-11", HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_aulas_para_substituir_endpoint(client):
    prof1 = CustomUser.objects.create_user(username='prof1', password='password123', tipo='professor')
    prof2 = CustomUser.objects.create_user(username='prof2', password='password123', tipo='professor')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'prof1', 'password': 'password123'})
    token = token_response.data['access']
    modalidade = Modalidade.objects.create(nome="Substituição")
    Aula.objects.create(modalidade=modalidade, data_hora="2026-01-01T10:00:00Z", status="Agendada").professores.set([prof1])
    Aula.objects.create(modalidade=modalidade, data_hora="2026-01-02T12:00:00Z", status="Agendada").professores.set([prof2])
    Aula.objects.create(modalidade=modalidade, data_hora="2024-01-03T14:00:00Z", status="Agendada").professores.set([prof2])
    Aula.objects.create(modalidade=modalidade, data_hora="2026-01-04T16:00:00Z", status="Cancelada").professores.set([prof2])
    url = reverse('scheduling:aulas-substituicao')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['professores'][0]['username'] == 'prof2'


@pytest.mark.django_db
# O @patch intercepta a chamada à API do Gemini e a substitui por um objeto simulado
@patch('reporting.services.genai.GenerativeModel')
def test_gerar_relatorio_ia_endpoint(mock_generative_model, client):
    """
    Testa o endpoint de geração de relatório com IA, simulando a API externa.
    """
    # 1. ARRANGE
    # Configura o mock para se comportar como a API real
    mock_model_instance = mock_generative_model.return_value
    mock_model_instance.generate_content.return_value.text = "**Relatório Simulado**"
    
    # Cria dados de teste
    user = CustomUser.objects.create_user(username='testuser', password='password123')
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'testuser', 'password': 'password123'})
    token = token_response.data['access']
    
    aluno = Aluno.objects.create(nome_completo="Aluno IA")
    modalidade = Modalidade.objects.create(nome="Aula IA")
    aula = Aula.objects.create(modalidade=modalidade, data_hora=timezone.now(), status="Realizada")
    aula.alunos.set([aluno])
    PresencaAluno.objects.create(aula=aula, aluno=aluno, status='presente')
    RelatorioAula.objects.create(aula=aula, conteudo_teorico="Teste")

    # 2. ACT
    url = reverse('scheduling:aluno-gerar-relatorio-ia', kwargs={'pk': aluno.pk})
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    # 3. ASSERT
    assert response.status_code == status.HTTP_200_OK
    # Verifica se a API do Gemini foi chamada
    mock_model_instance.generate_content.assert_called_once()
    # Verifica se a resposta contém o HTML convertido do nosso texto simulado
    assert "<strong>Relatório Simulado</strong>" in response.data['report_html']
