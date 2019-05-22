from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import Group

from users.models import Profile
from reestr.models import Criminals

# Create your models here.


class GroupAccess(models.Model):
    doc_id = models.ForeignKey(Criminals, verbose_name='Досье', on_delete=models.CASCADE)
    group_id = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Групповой доступ'
        verbose_name_plural = 'Групповой доступ'

    def __str__(self):
        return str(self.doc_id) + ' -- ' + str(self.group_id)

    def get_absolute_url(self):
        return reverse('group_access_url', kwargs={'pk_access': self.id})


class PersonAccess(models.Model):
    doc_id = models.ForeignKey(Criminals, verbose_name='Досье', on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, verbose_name='Пользователь', on_delete=models.CASCADE)
    special = models.BooleanField(default=False, verbose_name='Специальный допуск')

    class Meta:
        verbose_name = 'Персональный доступ'
        verbose_name_plural = 'Персональный доступ'

    def __str__(self):
        return str(self.doc_id) + " -- " + str(self.user_id)
