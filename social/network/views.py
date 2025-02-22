# views.py
from rest_framework.views import APIView
from rest_framework.viewsets import generics

from .models import Group, Message, UserProfile, GroupMember
from .serializers import (GroupSerializer, MessageSerializer, UserSerializer, LoginSerializer,
                          GroupMemberSerializer, GroupDetailSerializer, UserProfileListSerializers)
from rest_framework import permissions, status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except NameError:
            return Response({'detail': 'Ошибка в коде'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            return Response({'detail': 'Сервер не работает'}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user = serializer.validated_data
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh токен отсутствует"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Токен успешно добавлен в черный список"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": f"Ошибка: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileList(generics.ListAPIView):
    serializer_class = UserProfileListSerializers

    def get_queryset(self):
        return UserProfile.objects.filter(username=self.request.user.username)


class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer


class GroupMemberView(generics.ListCreateAPIView):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer


class GroupMemberRetrieve(generics.RetrieveDestroyAPIView):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        """Переопределяем метод создания, чтобы проверить членство в группе"""
        user = self.request.user
        group = serializer.validated_data['group']  # Получаем группу из запроса

        # Проверяем, состоит ли пользователь в группе
        if not GroupMember.objects.filter(group=group, users=user).exists():
            return Response(
                {"detail": "Вы не состоите в этой группе."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Если все ок — сохраняем сообщение
        serializer.save(author=user)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Group, GroupMember
from django.contrib.auth import get_user_model


class RemoveUserFromGroupView(APIView):
    def delete(self, request, group_id, user_id):
        # Получаем объект группы
        group = get_object_or_404(Group, id=group_id)

        # Получаем объект пользователя
        user = get_object_or_404(get_user_model(), id=user_id)

        # Получаем объект GroupMember для этой группы
        group_member = get_object_or_404(GroupMember, group=group)

        # Проверяем, состоит ли пользователь в группе
        if user not in group_member.users.all():
            return Response(
                {"detail": f"User {user.username} is not a member of the group."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаляем пользователя из группы
        group_member.users.remove(user)

        return Response(
            {"detail": f"User {user.username} has been removed from the group {group.room_group_name}."},
            status=status.HTTP_200_OK
        )

