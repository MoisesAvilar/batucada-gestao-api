import pytest
from rest_framework import status
from django.urls import reverse
from .models import CustomUser


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
