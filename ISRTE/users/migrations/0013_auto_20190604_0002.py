# Generated by Django 2.2 on 2019-06-03 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190603_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pass_change_date',
            field=models.DateTimeField(null=True, verbose_name='Время изменения пароля'),
        ),
    ]
