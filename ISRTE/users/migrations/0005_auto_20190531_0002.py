# Generated by Django 2.2 on 2019-05-30 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_role_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='auth.Group', verbose_name='Группа'),
        ),
    ]
