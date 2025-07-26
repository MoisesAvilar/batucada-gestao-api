from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer, ProfessorDetailSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    Endpoint de API para permitir que novos usuários se registrem.
    É um endpoint público (permission_classes = [permissions.AllowAny]).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({
                "user": user_data,
                "message": "Usuário do tipo 'aluno' criado com sucesso!"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de API que permite que professores sejam listados e visualizados.
    'ReadOnly' significa que não permite criação ou edição por aqui.
    """
    # O queryset base são todos os usuários que são professores ou admins
    queryset = CustomUser.objects.filter(tipo__in=['professor', 'admin']).order_by('username')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Usa o serializer de detalhe na ação 'retrieve' (ver um professor)
        e o serializer simples na ação 'list' (listar todos os professores).
        """
        if self.action == 'retrieve':
            return ProfessorDetailSerializer
        return UserSerializer
