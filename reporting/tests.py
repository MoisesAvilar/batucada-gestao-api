import pytest
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser
from scheduling.models import Aluno, Modalidade, Aula, RelatorioAula

@pytest.mark.django_db
def test_admin_dashboard_endpoint(client):
    """
    Testa o endpoint do dashboard do admin, verificando os KPIs agregados.
    """
    # 1. ARRANGE
    admin = CustomUser.objects.create_user(username='admin', password='password123', tipo='admin', is_staff=True)
    prof = CustomUser.objects.create_user(username='prof1', password='password123', tipo='professor')
    
    token_url = reverse('users:token_obtain_pair')
    token_response = client.post(token_url, {'username': 'admin', 'password': 'password123'})
    token = token_response.data['access']

    modalidade = Modalidade.objects.create(nome="Aula Teste")
    
    # Cria 3 aulas: 2 realizadas, 1 cancelada. 1 realizada pelo prof.
    aula1 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-01T10:00:00Z", status="Realizada")
    aula1.professores.set([prof])
    RelatorioAula.objects.create(aula=aula1, professor_que_validou=prof)
    
    aula2 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-02T10:00:00Z", status="Realizada")
    aula2.professores.set([prof]) # Atribuída, mas não validada por ele
    
    aula3 = Aula.objects.create(modalidade=modalidade, data_hora="2025-01-03T10:00:00Z", status="Cancelada")
    aula3.professores.set([prof])

    # 2. ACT
    url = reverse('reporting:admin-dashboard')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    # 3. ASSERT
    assert response.status_code == status.HTTP_200_OK

    # Verifica alguns dados chave
    kpis = response.data['kpis']
    assert kpis['total_aulas'] == 3
    assert kpis['total_realizadas'] == 2
    assert kpis['total_canceladas'] == 1
    
    prof_perf = response.data['professor_performance']
    assert len(prof_perf) == 1
    assert prof_perf[0]['username'] == 'prof1'
    assert prof_perf[0]['total_atribuidas'] == 3
    assert prof_perf[0]['total_realizadas'] == 1 # Apenas a que ele validou
