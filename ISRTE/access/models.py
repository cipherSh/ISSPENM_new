from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import Group

from users.models import Profile
from reestr.models import Criminals

# Create your models here.


class GroupAccess(models.Model):
    doc_id = models.ForeignKey(Criminals, verbose_name='Досье', on_delete=models.CASCADE)
    group_id = models.ForeignKey(Group, verbose_name='Группа', on_delete=models.CASCADE)
    add = models.BooleanField(default=False, verbose_name='Права на добавление')
    update = models.BooleanField(default=False, verbose_name='Права на изменение')
    execute = models.BooleanField(default=False, verbose_name='Права на выполнение')

    class Meta:
        verbose_name = 'Групповой доступ'
        verbose_name_plural = 'Групповой доступ'

    def __str__(self):
        return str(self.doc_id) + ' -- ' + str(self.group_id)

    def get_absolute_url(self):
        return reverse('group_access_update_url', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('group_access_update_url', kwargs={'pk': self.id})


class PersonAccess(models.Model):
    doc_id = models.ForeignKey(Criminals, verbose_name='Досье', on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, verbose_name='Пользователь', on_delete=models.CASCADE)
    add_access = models.BooleanField(default=False, verbose_name='Права на добавление')
    update = models.BooleanField(default=False, verbose_name='Права на изменение')
    execute_access = models.BooleanField(default=False, verbose_name='Права на выполнение')
    special = models.BooleanField(default=False, verbose_name='Специальный допуск')

    class Meta:
        verbose_name = 'Персональный доступ'
        verbose_name_plural = 'Персональный доступ'

    def __str__(self):
        return str(self.doc_id) + " -- " + str(self.user_id)

    def get_update_url(self):
        return reverse('personal_access_update_url', kwargs={'pk': self.id})


class RequestToOpen(models.Model):
    doc = models.ForeignKey(Criminals, verbose_name='Досье', on_delete=models.CASCADE)
    group = models.BooleanField(verbose_name='Групповой доступ')
    user_id = models.ForeignKey(Profile, null=True, blank=True, verbose_name='Запрашиваемый человек', on_delete=models.CASCADE)
    group_id = models.ForeignKey(Group, null=True, blank=True, verbose_name='Запрашиваемая группа', on_delete=models.CASCADE)
    reason_open = models.TextField(max_length=1000, verbose_name='Причина запроса')
    date_request = models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')
    check = models.BooleanField(verbose_name='Обработано')
    accept = models.BooleanField(verbose_name='Открыть доступ')
    reason_reject = models.TextField(null=True, blank=True, verbose_name='Причина отклонение')

    class Meta:
        verbose_name = "Запрос на доступ"
        verbose_name_plural = "Запросы на доступ"

    def __str__(self):
        if self.group:
            return str(self.doc) + " -- " + str(self.group_id)
        return str(self.doc) + " -- " + str(self.user_id)

    def get_accept_url(self):
        return reverse('request_accept_url', kwargs={'pk': self.id})

    def get_reject_url(self):
        return reverse('request_reject_url', kwargs={'pk': self.id})


