# Generated by Django 2.2 on 2019-05-31 15:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20190531_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogs',
            name='message',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}, verbose_name='Сообщение'),
        ),
    ]