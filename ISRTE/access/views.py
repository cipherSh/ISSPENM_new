from django.shortcuts import render, redirect, HttpResponse, reverse
from django.views.generic import View
from datetime import datetime

# forms

from .forms import GroupAccessForm, PersonalAccessForm, GroupAccessUpdateForm, PersonalAccessUpdateForm, \
    RequestToOpenAccessForm, RequestToOpenAcceptForm, RequestToOpenRejectForm, RequestToOpenGroupAccessForm, \
    RequestToOpenGroupAcceptForm

# models

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import PersonAccess, GroupAccess, RequestToOpen
from reestr.models import Criminals
from users.models import UserLogs

# views
from users.views import action_logging_view, action_logging_update, action_logging_create, action_logging_delete, \
    action_logging_added


# Create your views here.


def determinate_owner_or_superuser(request, criminal):
    if request.user.is_superuser or criminal.owner == request.user.profile:
        return True
    return False


def determinate_have_access(request, criminal):
    user_group = request.user.groups.all()
    ans = False
    for group in user_group:
        if GroupAccess.objects.filter(doc_id=criminal).filter(group_id=group):
            ans = True

    if request.user.is_superuser or criminal.owner == request.user.profile:
        return True
    elif PersonAccess.objects.filter(doc_id=criminal).filter(user_id=request.user.profile):
        if request.user.profile.trust_level_id.level >= criminal.confident.level:
            if criminal.close:
                if PersonAccess.objects.filter(doc_id=criminal).filter(user_id=request.user.profile).filter(
                        special=True):
                    return True
                return False
            return True
        return False
    elif ans:
        if request.user.profile.trust_level_id.level >= criminal.confident.level:
            return True
        return False
    else:
        return False


def assign_full_access(request):
    view_criminals = Permission.objects.get(codename="view_criminals")
    change_criminals = Permission.objects.get(codename="change_criminals")
    execute_criminals = Permission.objects.get(codename="execute_criminals")
    add_detail = Permission.objects.get(codename='add_detail')
    request.user.user_permissions.add(change_criminals, execute_criminals, view_criminals, add_detail)
    return request


def access_determinate(request, criminal):
    view_criminals = Permission.objects.get(codename="view_criminals")
    change_criminals = Permission.objects.get(codename="change_criminals")
    execute_criminals = Permission.objects.get(codename="execute_criminals")
    add_detail = Permission.objects.get(codename='add_detail')

    if not request.user.is_superuser:
        if not criminal.owner == request.user.profile:
            pr = PersonAccess.objects.filter(doc_id=criminal).filter(user_id=request.user.profile)
            if pr:
                if pr.update:
                    request.user.user_permissions.add(change_criminals)
    return request


def access_list(request):
    group_access = GroupAccess.objects.all()
    person_access = PersonAccess.objects.all()
    docs_requests = RequestToOpen.objects.filter(check=False).filter(group=False).order_by('-date_request')
    docs_requests_group = RequestToOpen.objects.filter(check=False).filter(group_id=not None).order_by('-date_request')
    context = {
        'group_access': group_access,
        'person_access': person_access,
        'docs_requests': docs_requests,
        'docs_requests_group': docs_requests_group,
        'search_url': 'control_access_url'
    }
    return render(request, 'access/access_list.html', context=context)


class GroupAccessUpdate(View):
    def get(self, request, pk):
        doc = GroupAccess.objects.get(id=pk)
        form = GroupAccessUpdateForm(instance=doc)
        return render(request, 'access/group_access_create.html', context={'form': form, 'doc': doc})

    def post(self, request, pk):
        doc = GroupAccess.objects.get(id=pk)
        bound_form = GroupAccessUpdateForm(request.POST, instance=doc)

        if bound_form.is_valid():
            access = bound_form.save()
            action_logging_update(request, doc)
            return redirect('/access/')
        return render(request, 'access/group_access_create.html', context={'form': bound_form, 'doc': doc})


class PersonalAccessUpdate(View):
    def get(self, request, pk):
        doc = PersonAccess.objects.get(id=pk)
        form = PersonalAccessUpdateForm(instance=doc)
        return render(request, 'access/personal_access_create.html', context={'form': form, 'doc': doc})

    def post(self, request, pk):
        doc = PersonAccess.objects.get(id=pk)
        bound_form = PersonalAccessUpdateForm(request.POST, instance=doc)

        if bound_form.is_valid():
            access = bound_form.save()
            action_logging_update(request, doc)
            return redirect('/access/')
        return render(request, 'access/personal_access_create.html', context={'form': bound_form, 'doc': doc})


def group_access_delete(request, pk):
    access = GroupAccess.objects.get(id=pk)
    action_logging_delete(request, access)
    access.delete()
    return redirect('/access/')


def personal_access_delete(request, pk):
    access = PersonAccess.objects.get(id=pk)
    action_logging_delete(request, access)
    access.delete()
    return redirect('/access/')


class RequestToOpenPersonalAccess(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        form = RequestToOpenAccessForm()
        context = {
            'criminal': criminal,
            'form': form
        }
        return render(request, 'reestr/criminals/request_to_open_pa.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = RequestToOpenAccessForm(request.POST)

        if bound_form.is_valid():
            new_request = bound_form.save(commit=False)
            new_request.doc = criminal
            new_request.group = False
            new_request.user_id = request.user.profile
            new_request.check = False
            new_request.accept = False
            new_request.date_request = datetime.now()
            new_request.save()
            action_logging_create(request, new_request)
            return redirect(criminal)

        context = {
            'criminal': criminal,
            'form': bound_form
        }
        return render(request, 'reestr/criminals/request_to_open_pa.html', context=context)


class RequestToOpenGroupAccess(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        form = RequestToOpenGroupAccessForm()
        context = {
            'criminal': criminal,
            'form': form
        }
        return render(request, 'reestr/criminals/request_to_open_group.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = RequestToOpenGroupAccessForm(request.POST)

        if bound_form.is_valid():
            new_request = bound_form.save(commit=False)
            new_request.doc = criminal
            new_request.group = True
            new_request.user_id = request.user.profile
            new_request.check = False
            new_request.accept = False
            new_request.date_request = datetime.now()
            new_request.save()
            action_logging_create(request, new_request)
            return redirect(criminal)

        context = {
            'criminal': criminal,
            'form': bound_form
        }
        return render(request, 'reestr/criminals/request_to_open_group.html', context=context)


class GroupAccessCreate(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        form = GroupAccessForm()
        return render(request, 'access/group_access_create.html', context={'form': form, 'criminal': criminal})

    def post(self, request, pk):
        bound_form = GroupAccessForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_form.is_valid():
            new_access = bound_form.save(commit=False)
            new_access.doc_id = criminal
            old_access = GroupAccess.objects.filter(doc_id=new_access.doc_id).filter(group_id=new_access.group_id)
            if old_access:
                old_access.delete()
            new_access.save()
            action_logging_create(request, new_access)
            return redirect(criminal)
        return render(request, 'access/group_access_create.html', context={'form': bound_form, 'criminal': criminal})


class PersonalAccessCreate(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        form = PersonalAccessForm()
        return render(request, 'access/personal_access_create.html', context={'form': form, 'criminal': criminal})

    def post(self, request, pk):
        bound_form = PersonalAccessForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_form.is_valid():
            new_access = bound_form.save(commit=False)
            new_access.doc_id = criminal
            old_access = PersonAccess.objects.filter(doc_id=new_access.doc_id).filter(user_id=new_access.user_id)
            if old_access:
                old_access.delete()
            new_access.save()
            action_logging_create(request, new_access)
            return redirect(criminal)
        return render(request, 'access/personal_access_create.html', context={'form': bound_form, 'criminal': criminal})


class RequestToOpenAccept(View):
    def get(self, request, pk):
        request_to_open = RequestToOpen.objects.get(id=pk)
        form = RequestToOpenAcceptForm
        context = {
            'request_to_open': request_to_open,
            'form': form
        }
        return render(request, 'access/personal_access_create.html', context=context)

    def post(self, request, pk):
        bound_form = RequestToOpenAcceptForm(request.POST)
        request_to_open = RequestToOpen.objects.get(id=pk)
        context = {
            'request_to_open': request_to_open,
            'form': bound_form
        }

        if bound_form.is_valid():
            new_access = bound_form.save(commit=False)
            new_access.doc_id = request_to_open.doc
            new_access.user_id = request_to_open.user_id
            old_access = PersonAccess.objects.filter(doc_id=new_access.doc_id).filter(user_id=new_access.user_id)
            if old_access:
                old_access.delete()
            new_access.save()
            request_to_open.check = True
            request_to_open.accept = True
            request_to_open.date_check = datetime.now()
            request_to_open.save()
            action_logging_create(request, new_access)
            action_logging_update(request, request_to_open)
            return redirect('/')
        return render(request, 'access/personal_access_create.html', context=context)


class RequestToOpenGroupAccept(View):
    def get(self, request, pk):
        request_to_open = RequestToOpen.objects.get(id=pk)
        form = RequestToOpenGroupAcceptForm
        context = {
            'request_to_open': request_to_open,
            'form': form
        }
        return render(request, 'access/personal_access_create.html', context=context)

    def post(self, request, pk):
        bound_form = RequestToOpenGroupAcceptForm(request.POST)
        request_to_open = RequestToOpen.objects.get(id=pk)
        context = {
            'request_to_open': request_to_open,
            'form': bound_form
        }

        if bound_form.is_valid():
            new_access = bound_form.save(commit=False)
            new_access.doc_id = request_to_open.doc
            new_access.group_id = request_to_open.group_id
            old_access = GroupAccess.objects.filter(doc_id=new_access.doc_id).filter(group_id=new_access.group_id)
            if old_access:
                old_access.delete()
            new_access.save()
            request_to_open.check = True
            request_to_open.accept = True
            request_to_open.date_check = datetime.now()
            request_to_open.save()
            action_logging_create(request, new_access)
            action_logging_update(request, request_to_open)
            return redirect('/')
        return render(request, 'access/personal_access_create.html', context=context)


class RequestToOpenReject(View):
    def get(self, request, pk):
        request_to_open = RequestToOpen.objects.get(id=pk)
        form = RequestToOpenRejectForm
        context = {
            'request_to_open': request_to_open,
            'form': form
        }
        return render(request, 'access/request_reject.html', context=context)

    def post(self, request, pk):
        request_to_open = RequestToOpen.objects.get(id=pk)
        bound_form = RequestToOpenRejectForm(request.POST)
        context = {
            'request_to_open': request_to_open,
            'form': bound_form
        }

        if bound_form.is_valid():
            temp = bound_form.save(commit=False)
            request_to_open.reason_reject = temp.reason_reject
            request_to_open.check = True
            request_to_open.date_check = datetime.now()
            request_to_open.save()
            action_logging_update(request, request_to_open)
            return redirect('/registry/')
        return render(request, 'access/request_reject.html', context=context)
