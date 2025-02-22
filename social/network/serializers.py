# serializers.py
from rest_framework import serializers
from .models import Group, GroupMember, Message, UserProfile

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'date_registered']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username']


class GroupSerializer(serializers.ModelSerializer):
    author = UserProfileSerializers()

    class Meta:
        model = Group
        fields = ['id', 'author', 'room_group_name', 'image']


class GroupSimpleSerializer(serializers.ModelSerializer):
    author = UserProfileSerializers()

    class Meta:
        model = Group
        fields = ['id', 'author', 'room_group_name', 'image']


class GroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupMember
        fields = ['id', 'group','users', 'joined_at']


class GroupMemberSimpleSerializer(serializers.ModelSerializer):
    users = UserProfileSerializers(many=True)
    class Meta:
        model = GroupMember
        fields = ['id', 'users', 'joined_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'group', 'author', 'text', 'image', 'video', 'created_at']


class GroupDetailSerializer(serializers.ModelSerializer):
    author = UserProfileSerializers()
    members = GroupMemberSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ['id', 'author', 'room_group_name', 'image', 'members']


class UserProfileListSerializers(serializers.ModelSerializer):
    group_member = GroupMemberSerializer(read_only=True, many=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'group_member']
