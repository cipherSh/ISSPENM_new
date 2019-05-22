from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse

#from reestr.models import Criminals


class Role(models.Model):
    role_type = models.CharField(max_length=40, verbose_name="Тип пользователя")

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
        return reverse('user_profile_url', kwargs={'pk': self.user.id})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


