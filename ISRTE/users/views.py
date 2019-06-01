import json
from django.shortcuts import render, redirect, Http404, HttpResponse, reverse
from django.http import HttpResponseNotFound
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from datetime import datetime
from django.utils.timezone import get_current_timezone
from django.views.generic import View
from django.core.exceptions import ValidationError
import pytz

#models
from .models import Profile, Audit, UserLogs
from reestr.models import Criminals
from django.contrib.contenttypes.models import ContentType

# forms
from .forms import UserUpdateForm, ProfileUpdateForm


# Create your views here.


def login_view(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                Audit.objects.create(user=request.user.profile, act='Вход в систему', data=datetime.now(
                    tz=get_current_timezone()))
                return redirect("/")
            else:
                login_error = "Вам закрыто вход в систему"
                return render(request, "login.html", {"login_error": login_error})
        else:
            login_error = 'Введено неправильные данные'
            return render(request, "login.html", {"login_error": login_error})
    else:
        return render(request, "login.html")


def logout_view(request):
    Audit.objects.create(user=request.user.profile, act='Выход из системы', data=datetime.now(
                    tz=get_current_timezone()))
    logout(request)
    return redirect('/users/login/')


@login_required
def user_create(request):
    message = None
    context = {
        'wrapper_title': "Создание пользователя",
        'message': message
    }
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).count():
            message = "Пользователь c именем {} уже зарегистрирован".format(username)
            context = {
                'wrapper_title': "Создание пользователя",
                'message': message
            }
            return render(request, 'profiles/user_create.html', context=context)
        else:
            user = User.objects.create_user(username=username, password=password)
            profile = Profile.objects.get(user=user)
            action_logging_create(request, user)
            return redirect(profile)

    return render(request, 'profiles/user_create.html', context=context)


class UserUpdateView(View):
    def get(self, request, pk):
        profile = Profile.objects.get(id=pk)
        user_form = UserUpdateForm(instance=profile.user)
        profile_form = ProfileUpdateForm(instance=profile)
        context = {
            'wrapper_title': 'Обновление профиля пользователя',
            'profile': profile,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'profiles/profile_update.html', context=context)

    def post(self, request, pk):
        profile = Profile.objects.get(id=pk)
        bound_user_form = UserUpdateForm(request.POST, instance=profile.user)
        bound_profile_form = ProfileUpdateForm(request.POST, instance=profile)
        context = {
            'wrapper_title': 'Обновление профиля пользователя',
            'profile': profile,
            'user_form': bound_user_form,
            'profile_form': bound_profile_form
        }

        if bound_user_form.is_valid() and bound_profile_form.is_valid():
            up_user = bound_user_form.save()
            up_profile = bound_profile_form.save()
            if profile.role_id:
                last_group = profile.role_id.group
                new_group = up_profile.role_id.group
                up_profile.user.groups.remove(last_group)
                up_profile.user.groups.add(new_group)
            else:
                new_group = up_profile.role_id.group
                up_profile.user.groups.add(new_group)
            context = {
                'wrapper_title': 'Обновление профиля пользователя',
                'profile': up_profile
            }
            action_logging_update(request, profile)
            return render(request, 'profiles/success_create.html', context=context)
        return render(request, 'profiles/profile_update.html', context=context)





@login_required
def users_list(request):
    users_list = Profile.objects.all().order_by('role_id')
    search_query = request.GET.get('search_query_text', '')

    if search_query:
        users_list = Profile.objects.all().order_by('role_id')
    context = {
        'wrapper_title': "Пользователи",
        'search_url': 'users_list_url',
        "users": users_list
    }
    return render(request, "profiles/users_list.html", context)


@login_required
def user_profile(request, pk):
    profile = Profile.objects.get(id=pk)
    if request.user.has_perm('view_user') or request.user.profile == profile:

        user_docs = Criminals.objects.filter(owner=profile)
        #p_acc = PersonAccess.objects.filter(user_id=profile)
        if request.user.profile == profile:
            wrapper_title = "Мой профиль"
        else:
            wrapper_title = "Профиль пользователя"
        context = {
            'profile': profile,
            'user_docs': user_docs,
            'wrapper_title': wrapper_title,
            #'p_acc': p_acc
        }
        return render(request, 'profiles/user_profile.html', context=context)
    return HttpResponseNotFound('')


@login_required
def users_audit(request):
    audit = Audit.objects.all().order_by('-data')
    context = {
        'audit': audit,
        'wrapper_title': "Журнал авторизации"
    }
    return render(request, 'profiles/audit.html', context=context)


@login_required
def users_logs(request):
    logs = UserLogs.objects.all().order_by('-action_time')
    context = {
        'logs': logs,
        'wrapper_title': "Журнал действий"
    }
    return render(request, 'profiles/logs.html', context=context)


@login_required
def group_list(request):
    groups = Group.objects.all()
    context = {
        'wrapper_title': "Группы",
        'search_url': 'manhunt_list_url',
        "groups": groups
    }
    return render(request, "profiles/group_list.html", context=context)


def inactive_user(request, pk):
    profile = Profile.objects.get(id=pk)
    log_message = ''
    if profile.user.is_active:
        profile.user.is_active = False
        profile.user.save()
        log_message = 'Доступ к систему закрыть'
    else:
        profile.user.is_active = True
        profile.user.save()
        log_message = 'Доступ к систему открыть'
    action_logging_other(request, profile, log_message)
    return redirect(profile)


@login_required
def profile_logs(request, pk):
    profile = Profile.objects.get(id=pk)
    logs = object_logs(request, profile)
    context = {
        'profile': profile,
        'logs': logs,
        'wrapper_title': 'Пользователи'
    }
    return render(request, 'reestr/logs/criminal_logs.html', context=context)


@login_required
def user_acts(request, pk):
    profile = Profile.objects.get(id=pk)
    acts = UserLogs.objects.filter(user=profile)
    context = {
        'profile': profile,
        'logs': acts,
        'wrapper_title': 'Пользователи'
    }
    return render(request, 'profiles/user_logs.html', context=context)




def object_logs(request, object):
    content_type = ContentType.objects.get_for_model(object)
    logs = UserLogs.objects.filter(content_type=content_type).filter(object_id=object.id)
    return logs


# logging

def action_logging_create(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=1, message={'create': {}},
                                  content_type=content_type, user=request.user.profile)


def action_logging_view(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=2, message={'view': {}}, content_type=content_type,
                                  user=request.user.profile)


def action_logging_update(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=3, message={'update': {}},
                                  content_type=content_type, user=request.user.profile)


def action_logging_delete(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=4, message={'delete': {}},
                                  content_type=content_type, user=request.user.profile)


def action_logging_added(request, object, addedobject):
    content_type = ContentType.objects.get_for_model(object)
    ao_content_type = ContentType.objects.get_for_model(addedobject)
    ao_name = ao_content_type.name
    ob = addedobject
    mes = {'added': {ao_name: str(ob)}}
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=5, message=mes,
                                  content_type=content_type, user=request.user.profile)


def action_logging_exclude(request, object, excludedobject):
    content_type = ContentType.objects.get_for_model(object)
    ao_content_type = ContentType.objects.get_for_model(excludedobject)
    ao_name = ao_content_type.name
    ob = excludedobject
    mes = {'exclude': {ao_name: str(ob)}}
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=6, message=mes,
                                  content_type=content_type, user=request.user.profile)


def action_logging_other(request, object, message):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=7, message=message,
                                  content_type=content_type, user=request.user.profile)
