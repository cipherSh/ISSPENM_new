from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.contrib.auth.models import ContentType, Group

#from reestr.models import Criminals


class Role(models.Model):
    role_type = models.CharField(max_length=40, verbose_name="Тип пользователя")
    group = models.ForeignKey(Group, on_delete=models.PROTECT, default=1, verbose_name='Группа')

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Таблица ролей"

    def __str__(self):
        return self.role_type


class TrustLevel(models.Model):
    trust_level = models.CharField(max_length=200, verbose_name='Уровень доверия/конфиденциальность')
    level = models.IntegerField(verbose_name='Уровень', unique=True)

    def __str__(self):
        return self.trust_level


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_id = models.ForeignKey(Role, verbose_name='Роль пользователя', on_delete=models.SET_NULL, null=True)
    trust_level_id = models.ForeignKey(TrustLevel, verbose_name='Уровень доверия', on_delete=models.SET_NULL, null=True,
                                       blank=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name

    def get_absolute_url(self):
        return reverse('user_update_url', kwargs={'pk': self.user.id})

    def get_update_url(self):
        return reverse('user_profile_url', kwargs={'pk': self.user.id})

    def get_logs_url(self):
        return reverse('profile_logs_url', kwargs={'pk': self.user.id})

    def get_user_logs_url(self):
        return reverse('user_acts_url', kwargs={'pk': self.user.id})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Audit(models.Model):
    user = models.ForeignKey(Profile, verbose_name='Пользователь', null=True, on_delete=models.PROTECT)
    act = models.CharField(max_length=200, verbose_name='Действие')
    data = models.DateTimeField(verbose_name='Дата')

    class Meta:
        verbose_name = "Аудит входа и выхода"
        verbose_name_plural = "Аудит входа и выхода"
        ordering = ['-data']

    def __str__(self):
        return str(self.data) + ' --- ' + str(self.user) + ' --- ' + self.act


def get_default_message():
    return {''}


class UserLogs(models.Model):
    action_time = models.DateTimeField(verbose_name='Дата и время')
    object_id = models.CharField(max_length=40, verbose_name="ID объекта", null=True)
    object_repr = models.CharField(max_length=200, verbose_name='Объект')
    action_flag = models.SmallIntegerField(verbose_name='Код действия')
    message = JSONField(verbose_name='Сообщение', default=get_default_message)
    content_type = models.ForeignKey(ContentType, verbose_name='Номер контента', on_delete=models.PROTECT)
    user = models.ForeignKey(Profile, verbose_name='Пользователь', null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Журнал регистрации действий пользователей'
        ordering = ['-action_time']

    def __str__(self):
        return str(self.action_time) + ' -- ' + str(self.object_repr) + ' -- ' + str(self.user)


