# Generated by Django 2.2 on 2019-05-27 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0006_requesttoopen_date_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='requesttoopen',
            name='date_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата обработки запроса'),
        ),
    ]