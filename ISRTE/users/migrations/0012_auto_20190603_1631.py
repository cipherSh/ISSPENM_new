# Generated by Django 2.2 on 2019-06-03 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20190603_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pass_change_date',
            field=models.DateField(null=True, verbose_name='Время изменения пароля'),
        ),
    ]
