import json
from django.shortcuts import render, redirect, Http404, HttpResponse, reverse
from django.http import HttpResponseNotFound
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from datetime import datetime, timedelta, date
from django.utils.timezone import get_current_timezone
from django.utils import timezone
from django.views.generic import View
from django.core.paginator import Paginator
from io import BytesIO
from reportlab.pdfgen import canvas
import pytz

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# models

from .models import Profile, Audit, UserLogs
from reestr.models import Criminals
from django.contrib.contenttypes.models import ContentType

# forms

from .forms import UserUpdateForm, ProfileUpdateForm, UserLogsSearchForm
from django.contrib.auth.forms import PasswordChangeForm


# Create your views here.

# Функция авторизации
def login_view(request):
    if request.POST:
        # Если пришел POST запрос
        # Вывод данных из post-запроса
        username = request.POST['username']
        password = request.POST['password']
        # Проверка наличия пользователя в системе
        user = authenticate(username=username, password=password)
        if user is not None:
            # Еcли пользователь зарегистрирован в системе
            if user.is_active:# Проверка доступа пользователя к систему
                # Если у пользователя есть доступ к системе
                login(request, user)# авторизация пользователя
                Audit.objects.create(user=request.user.profile, act='Вход в систему', data=datetime.now(
                    tz=get_current_timezone()))# Запись в журнал действий пользователя
                if request.user.profile.initial_pass:
                    # Если пароль пользователя является начальной
                    return redirect(reverse('change_initial_pass_url'))# Вызов функции смены пароля
                key_term = timezone.now() - timedelta(minutes=60*24*30)# Нахождение даты 30 дней назад
                if key_term >= request.user.profile.pass_change_date:
                    # Если срок пароля истек
                    return redirect(reverse('change_initial_pass_url'))# Вызов функции смены пароля
                return redirect("/")# Переход в главную страницу
            else:
                # Если у пользователя нет доступа к системе
                login_error = "Вам закрыто вход в систему" # сообщение с ощибкой
                return render(request, "login.html", {"login_error": login_error})# Переход в форму авторизации
        else:
            # Еcли пользователь не зарегистрирован в системе
            login_error = 'Введено неправильные данные'
            return render(request, "login.html", {"login_error": login_error})
    else:
        # Если пришел GET запрос
        return render(request, "login.html")# Переход в форму авторизации

# Функция LOGOUT
def logout_view(request):
    # Запись в журнале действии
    Audit.objects.create(user=request.user.profile, act='Выход из системы', data=datetime.now(
        tz=get_current_timezone()))
    logout(request)# Удаление сессии
    return redirect('/users/login/')# Переход в форму авторизации

# Функция регистрации пользователя
@login_required # Проверка авторизован ли пользователь
def user_create(request):
    message = None
    context = {
        'wrapper_title': "Создание пользователя",
        'message': message
    }
    if request.POST:
        # Если пришел POST запрос
        # Вывод имени пользователя из post-запроса
        username = request.POST['username']
        # Генерация начального пароля
        password = User.objects.make_random_password(15)

        # Если пользователь зарегистрирован в системе
        if User.objects.filter(username=username).count():
            # Сообщение с ошибкой
            message = "Пользователь c именем {} уже зарегистрирован".format(username)
            context = {
                'wrapper_title': "Создание пользователя",
                'message': message
            }
            # Переход в форму регистрации
            return render(request, 'profiles/user_create.html', context=context)

        # Если не задано имени пользователя
        elif username == '':
            message = "Пожалуйста введите имени пользователя!"
            context = {
                'wrapper_title': "Создание пользователя",
                'message': message
            }
            return render(request, 'profiles/user_create.html', context=context)
        else:
            # Запись в базе данных
            user = User.objects.create_user(username=username, password=password)
            profile = Profile.objects.get(user=user)
            # Галочка на поле начального пароля
            user.profile.initial_pass = True
            # Дата последнего изменение пароля
            user.profile.pass_change_date = datetime.now()
            user.profile.save()
            # Запись в журнале действий пользователя
            action_logging_create(request, user)
            context = {
                'wrapper_title': "Создание пользователя",
                'user': user,
                'password': password
            }
            return render(request, 'profiles/success_create.html', context=context)

    return render(request, 'profiles/user_create.html', context=context)

# Функция изменение начального пароля
@login_required # Проверка авторизован ли пользователь
def change_initial_pass(request):
    error_message = ''
    message = ''
    # Если пароль явялется начальным
    if request.user.profile.initial_pass:
        message = 'Пожалуйста измените начальный пароль'
    else:
        message = 'Срок пароля истек. Пожалуйста измените пароль'
    # Если пришел POST запрос
    if request.POST:
        password = request.POST['password']
        confirm = request.POST['confirm']
        # Проверка паролей на совпадение
        if password == confirm:
            u = request.user
            u.set_password(password)
            u.profile.initial_pass = False
            u.profile.pass_change_date = timezone.now()
            u.save()
            # обновление сессии пользователя
            update_session_auth_hash(request, u)
            log_message = 'Начальный пароль изменен'
            # запись в журнале
            action_logging_other(request, u.profile, log_message)
            # Главная страница
            return redirect('/')
        else:
            error_message = 'Пароли не совпадает. Пожалуйста введите пароль еще раз'
    context = {
        'wrapper_title': 'Изменение пароля',
        'error_message': error_message,
        'message': message
    }
    # форма изменение пароля
    return render(request, 'profiles/change_initial_pass.html', context=context)

# Функция обновление профиля пользователя

class UserUpdateView(View):
    # Вывод форму обновление профиля пользователя
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
    # обновление данных пользователя
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

        # если введено правильные данные
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
            # Запись в журнал
            action_logging_update(request, profile)
            return redirect(profile)
        # Если введено неправильные данные
        return render(request, 'profiles/profile_update.html', context=context)

# Функция изменение пароля
@login_required
def password_edit(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновление сессии пользователя
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль успешно изменен!')
            # переход в профиль пользователя
            return redirect(request.user.profile)
        else:
            messages.error(request, 'Исправьте ошибки!')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profiles/password_edit.html', {
        'form': form, 'wrapper_title': 'Изменение пароля'
    })

# Функция вывода списка пользователей
@login_required
def users_list(request):
    # Проверка явялется ли пользователь администратором
    if request.user.is_superuser:
        # Список пользователей
        users_list = Profile.objects.all().order_by('role_id')
        # Поисковый запрос, если нет то пустое значение
        search_query = request.GET.get('search_query_text', '')

        # Если пришел поисковый запрос
        if search_query:
            users_list = Profile.objects.all().order_by('role_id')
        context = {
            'wrapper_title': "Пользователи",
            'search_url': 'users_list_url',
            "users": users_list
        }
        return render(request, "profiles/users_list.html", context)
    # Если пользователь не явяляется алминистратором
    return HttpResponseNotFound('')


# Функция вывода профиля поьзователя
@login_required
def user_profile(request, pk):
    # данные пользователя
    profile = Profile.objects.get(id=pk)
    # проверка есть ли у пользователя права на просмотр профиля пользователя
    if request.user.has_perm('view_user') or request.user.profile == profile:
        #Список документов пользователя
        user_docs = Criminals.objects.filter(owner=profile)
        # p_acc = PersonAccess.objects.filter(user_id=profile)
        if request.user.profile == profile:
            wrapper_title = "Мой профиль"
        else:
            wrapper_title = "Профиль пользователя"
        context = {
            'profile': profile,
            'user_docs': user_docs,
            'wrapper_title': wrapper_title,
            # 'p_acc': p_acc
        }
        return render(request, 'profiles/user_profile.html', context=context)
    # если у пользователя нету прав на просмотр профиля пользователя
    return HttpResponseNotFound('')

# Удаление пользователя
@login_required
def user_delete(request, pk):
    profile = Profile.objects.get(id=pk)
    profile.user.delete()
    return redirect(reverse('users_list_url'))

# Функция вывода журнал вход\выхода
@login_required
def users_audit(request):
    audit = Audit.objects.all().order_by('-data')

    # разделение весь журнал на страницы
    paginator = Paginator(audit, 20)
    page_number = request.GET.get('page', 1)
    # страницы
    page = paginator.get_page(page_number)
    # если есть другие страницы
    is_paginated = page.has_other_pages()
    # проверка есть ли предыдущая страница
    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''
    start_url = 1
    last_url = ''
    # Данные передаваемые в страницу
    context = {
        'audit': page,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'start_url': start_url,
        'last_url': last_url,
        'wrapper_title': "Журнал авторизации"
    }
    return render(request, 'profiles/audit.html', context=context)


# журнал действий
@login_required
def users_logs(request):
    search_form = UserLogsSearchForm()
    logs = ''
    if request.POST:
        bound_form = UserLogsSearchForm(request.POST)
        if bound_form.is_valid():
            search = bound_form.save(commit=False)
            search_query = search.user
            logs = UserLogs.objects.filter(user=search_query).order_by('-action_time')
    else:
        logs = UserLogs.objects.all().order_by('-action_time')

    # Постраничный вывод данных
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''
    # Данные передаваемые в страницу
    context = {
        'logs': page,
        'search_form': search_form,
        'is_paginated': is_paginated,
        'next_url': next_url,
        'prev_url': prev_url,
        'wrapper_title': "Журнал действий"
    }
    return render(request, 'profiles/logs.html', context=context)

# Функция вывода список групп
@login_required
def group_list(request):
    # список групп
    groups = Group.objects.all()
    # Данные передаваемые в страницу
    context = {
        'wrapper_title': "Группы",
        'search_url': 'manhunt_list_url',
        "groups": groups
    }
    return render(request, "profiles/group_list.html", context=context)

# Функция предоставление доступа к систему
@login_required
def inactive_user(request, pk):
    # пользователь
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
    # Запсиь в журнале
    action_logging_other(request, profile, log_message)
    return redirect(profile)

# Функция вывода логи пользователя для конкретного объекта
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


# Функция вывода логи пользователя
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

# Логи объекта
def object_logs(request, object):
    content_type = ContentType.objects.get_for_model(object)
    logs = UserLogs.objects.filter(content_type=content_type).filter(object_id=object.id)
    return logs


# Логгирование
# Запись в журнале при создание какого объекта
def action_logging_create(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=1, message={'create': {}},
                                  content_type=content_type, user=request.user.profile)

# Запись в журнале при просмотре объекта
def action_logging_view(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=2, message={'view': {}}, content_type=content_type,
                                  user=request.user.profile)

# Запись в журнале при изменении объекта
def action_logging_update(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=3, message={'update': {}},
                                  content_type=content_type, user=request.user.profile)

# Запись в журнале при удаление объекта
def action_logging_delete(request, object):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=4, message={'delete': {}},
                                  content_type=content_type, user=request.user.profile)

# Запись в журнале при добавление данных к объекту
def action_logging_added(request, object, addedobject):
    content_type = ContentType.objects.get_for_model(object)
    ao_content_type = ContentType.objects.get_for_model(addedobject)
    ao_name = ao_content_type.name
    ob = addedobject
    mes = {'added': {ao_name: str(ob)}}
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=5, message=mes,
                                  content_type=content_type, user=request.user.profile)

# Запись в журнале при удаление данных с объекта
def action_logging_exclude(request, object, excludedobject):
    content_type = ContentType.objects.get_for_model(object)
    ao_content_type = ContentType.objects.get_for_model(excludedobject)
    ao_name = ao_content_type.name
    ob = excludedobject
    mes = {'exclude': {ao_name: str(ob)}}
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=6, message=mes,
                                  content_type=content_type, user=request.user.profile)

# Запись в журнале в других случаях
def action_logging_other(request, object, message):
    content_type = ContentType.objects.get_for_model(object)
    log = UserLogs.objects.create(action_time=datetime.now(tz=get_current_timezone()), object_id=object.id,
                                  object_repr=object, action_flag=7, message=message,
                                  content_type=content_type, user=request.user.profile)

# формирование PDF файл с начальным паролем пользователя
def user_initial_pass(request, profile, password):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=profile.user.username'
    print('i am')
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(50, 790, "OPKK")
    p.drawString(10, 770, "Username:")
    p.drawString(100, 770, profile.user.username)
    p.drawString(10, 750, "Password:")
    p.drawString(100, 750, password)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def some_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="akylbekov.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(50, 790, "OPKK")
    p.drawString(100, 780, "Password was dropped")
    p.drawString(10, 770, "Username:")
    p.drawString(100, 770, "akylbekov")
    p.drawString(10, 750, "Password:")
    p.drawString(100, 750, "GDnNS7R2q5SaJE5")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
