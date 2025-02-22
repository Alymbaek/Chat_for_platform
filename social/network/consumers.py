import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message, Group, GroupMember, UserProfile
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f'group_{self.group_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
            return

        is_member = await self.is_user_in_group(self.user.id, self.group_id)
        if not is_member:
            await self.close()
            return

        # Удаляем старое соединение (если юзер уже в группе)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # Присоединяемся к группе
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            print("📩 Полученные данные:", repr(text_data))  # Выведет raw-данные
            text_data_json = json.loads(text_data.strip())  # Убираем лишние пробелы и переносы строк

            message = text_data_json.get('message')
            user_id = text_data_json.get('user_id')

            if not message or not user_id:
                return

            user = await self.get_user(user_id)
            group = await self.get_group(self.group_id)

            await self.save_message(group, user, message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user_id,
                    'username': user.username
                }
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await self.send(text_data=json.dumps({"error": f"Unexpected error: {str(e)}"}))

    async def chat_message(self, event):
        # Отправляем сообщение всем подключённым пользователям
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username']
        }))

    @sync_to_async(thread_sensitive=True)
    def is_user_in_group(self, user_id, group_id):
        """ Проверяет, состоит ли пользователь в группе """
        return GroupMember.objects.filter(group_id=group_id, users__id=user_id).exists()

    @sync_to_async(thread_sensitive=True)
    def get_user(self, user_id):
        return UserProfile.objects.get(id=user_id)

    @sync_to_async(thread_sensitive=True)
    def get_group(self, group_id):
        return Group.objects.get(id=group_id)

    @sync_to_async(thread_sensitive=True)
    def save_message(self, group, user, message):
        Message.objects.create(group=group, author=user, text=message)
