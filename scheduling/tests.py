import pytest
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser


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
