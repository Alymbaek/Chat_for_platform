from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class UserProfile(AbstractUser):
    date_registered = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username


# THIS CHAT

class Group(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room_group_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='image_group/', null=True, blank=True)

    def __str__(self):
        return self.room_group_name


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_member')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.users} in {self.group}"


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='message_image', null=True, blank=True)
    video = models.FileField(upload_to='message_video', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
