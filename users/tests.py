import pytest
from rest_framework import status
from django.urls import reverse
from .models import CustomUser
from scheduling.models import Aula, Aluno, Modalidade, RelatorioAula


# O marcador @pytest.mark.django_db garante que o banco de dados
# de teste seja criado e limpo para esta função.
@pytest.mark.django_db
def test_user_can_register_successfully(client):
    """
    Garante que um novo usuário pode ser registrado com sucesso.
    """
    url = reverse('users:register')
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'StrongPassword123!',
        'password2': 'StrongPassword123!'
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.count() == 1
    
    user = CustomUser.objects.get()
    assert user.username == 'testuser'
    assert user.tipo == 'aluno'


@pytest.mark.django_db
def test_registration_fails_if_passwords_do_not_match(client):
    """
    Garante que o registro falha se as senhas não coincidirem.
    """
    url = reverse('users:register')
    data = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'StrongPassword123!',
        'password2': 'DIFFERENTPassword123!'
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert CustomUser.objects.count() == 0
    assert 'password' in response.data


@pytest.mark.django_db
def test_professor_detail_endpoint_returns_kpis(client):
    """
    Testa se o endpoint de detalhe do professor retorna os KPIs corretos.
    """
    # 1. ARRANGE
    admin_user = CustomUser.objects.create_user(username='admin', password='password123', tipo='admin')
    prof1 = CustomUser.objects.create_user(username='prof1', password='password123', tipo='professor')
    prof2 = CustomUser.objects.create_user(username='prof2', password='password123', tipo='professor')
    
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'admin', 'password': 'password123'})
    token = token_response.data['access']

    modalidade = Modalidade.objects.create(nome="Aula Normal")
    modalidade_ac = Modalidade.objects.create(nome="Atividade Complementar")

    # Cenário 1: Aula normal realizada pelo prof1
    aula1 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-01T10:00:00Z", status="Realizada")
    aula1.professores.set([prof1])
    RelatorioAula.objects.create(aula=aula1, professor_que_validou=prof1)

    # Cenário 2: Aula agendada para o prof1
    aula2 = Aula.objects.create(modalidade=modalidade, data_hora="2026-01-02T10:00:00Z", status="Agendada")
    aula2.professores.set([prof1])

    # Cenário 3: prof1 foi substituído pelo prof2
    aula3 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-03T10:00:00Z", status="Realizada")
    aula3.professores.set([prof1])
    RelatorioAula.objects.create(aula=aula3, professor_que_validou=prof2)

    # Cenário 4: prof1 substituiu o prof2
    aula4 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-04T10:00:00Z", status="Realizada")
    aula4.professores.set([prof2])
    RelatorioAula.objects.create(aula=aula4, professor_que_validou=prof1)

    # 2. ACT
    url = reverse('users:professor-detail', kwargs={'pk': prof1.pk})
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    # 3. ASSERT
    assert response.status_code == status.HTTP_200_OK
    
    kpis = response.data['kpis']
    assert kpis['total_realizadas'] == 2 # aula1 + aula4
    assert kpis['total_agendadas'] == 1 # aula2
    assert kpis['total_substituicoes_feitas'] == 1 # aula4
    assert kpis['total_substituicoes_sofridas'] == 1 # aula3
