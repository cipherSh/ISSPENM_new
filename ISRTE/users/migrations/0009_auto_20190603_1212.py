# Generated by Django 2.2 on 2019-06-03 06:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190531_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='initial_pass',
            field=models.BooleanField(default=False, verbose_name='Начальный пароль'),
        ),
        migrations.AddField(
            model_name='profile',
            name='pass_change_date',
            field=models.DateField(default=datetime.datetime(2019, 6, 3, 12, 12, 12, 460496), verbose_name='Время изменения пароля'),
        ),
    ]