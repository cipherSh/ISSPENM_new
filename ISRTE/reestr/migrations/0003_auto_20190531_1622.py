# Generated by Django 2.2 on 2019-05-31 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reestr', '0002_auto_20190525_1510'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contacttype',
            options={'ordering': ['type_contact'], 'verbose_name': 'Тип контакт', 'verbose_name_plural': 'Типы контакта'},
        ),
        migrations.AlterModelOptions(
            name='criminaladdresses',
            options={'ordering': ['criminal_id'], 'verbose_name': 'Адрес', 'verbose_name_plural': 'Адреса'},
        ),
        migrations.AlterModelOptions(
            name='criminalcasecriminals',
            options={'verbose_name': 'Фигурант УД', 'verbose_name_plural': 'Фигуранты УД'},
        ),
        migrations.AlterModelOptions(
            name='criminals',
            options={'ordering': ['last_name', 'first_name', 'patronymic'], 'verbose_name': 'Досье', 'verbose_name_plural': 'Реестр'},
        ),
        migrations.AlterModelOptions(
            name='occupation',
            options={'verbose_name': 'Тип деятельноти', 'verbose_name_plural': 'Тип деятельности'},
        ),
        migrations.AlterModelOptions(
            name='personaddresses',
            options={'ordering': ['person_id'], 'verbose_name': 'Адрес гражданина', 'verbose_name_plural': 'Адрес граждан'},
        ),
        migrations.AlterModelOptions(
            name='persons',
            options={'ordering': ['last_name', 'first_name', 'patronymic'], 'verbose_name': 'Персона', 'verbose_name_plural': 'Гражданины'},
        ),
        migrations.AlterModelOptions(
            name='relativerelation',
            options={'ordering': ['type'], 'verbose_name': 'Родственное отношение', 'verbose_name_plural': 'Родственные отношении'},
        ),
        migrations.AlterField(
            model_name='criminaladdresses',
            name='kind',
            field=models.CharField(choices=[('residence', 'Место проживание'), ('registration', 'Место прописки')], default='registration', max_length=20, verbose_name='Тип адреса'),
        ),
    ]
