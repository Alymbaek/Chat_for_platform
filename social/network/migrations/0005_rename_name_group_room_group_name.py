# Generated by Django 5.1.6 on 2025-02-17 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_rename_user_groupmember_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='name',
            new_name='room_group_name',
        ),
    ]
