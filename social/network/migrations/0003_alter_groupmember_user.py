# Generated by Django 5.1.6 on 2025-02-16 12:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_alter_groupmember_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmember',
            name='user',
            field=models.ManyToManyField(related_name='group_member', to=settings.AUTH_USER_MODEL),
        ),
    ]
