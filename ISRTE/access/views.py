from django.shortcuts import render, redirect
from django.views.generic import View

from .forms import GroupAccessForm, PersonalAccessForm, GroupAccessUpdateForm, PersonalAccessUpdateForm

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import PersonAccess, GroupAccess
from reestr.models import Criminals


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
    context = {
        'group_access': group_access,
        'person_access': person_access
    }
    return render(request, 'access/access_list.html', context=context)


class GroupAccessUpdate(View):
    def get(self, request, pk):
        doc = GroupAccess.objects.get(id=pk)
        form = GroupAccessUpdateForm(instance=doc)
        return render(request, 'access/group_access_create.html', context={'form': form, 'doc': doc})

    def post(self, request, pk):
        doc = GroupAccess.objects.get(id=pk)
        bound_form = GroupAccessUpdateForm(request.POST)

        if bound_form.is_valid():
            doc.delete()
            access = bound_form.save()
            return redirect('/access/')
        return render(request, 'access/group_access_create.html', context={'form': bound_form, 'doc': doc})


class PersonalAccessUpdate(View):
    def get(self, request, pk):
        doc = PersonAccess.objects.get(id=pk)
        form = PersonalAccessUpdateForm(instance=doc)
        return render(request, 'access/personal_access_create.html', context={'form': form, 'doc': doc})

    def post(self, request, pk):
        doc = PersonAccess.objects.get(id=pk)
        bound_form = PersonalAccessUpdateForm(request.POST)

        if bound_form.is_valid():
            doc.delete()
            access = bound_form.save()
            return redirect('/access/')
        return render(request, 'access/personal_access_create.html', context={'form': bound_form, 'doc': doc})


def group_access_delete(request, pk):
    access = GroupAccess.objects.get(id=pk)
    access.delete()
    return redirect('/access/')


def personal_access_delete(request, pk):
    access = PersonAccess.objects.get(id=pk)
    access.delete()
    return redirect('/access/')


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
            if GroupAccess.objects.filter(group_id=new_access.group_id).filter(doc_id=new_access.doc_id):
                gr = GroupAccess.objects.filter(group_id=new_access.group_id).filter(doc_id=new_access.doc_id)
                return redirect('/access/group/<int:pk>/', pk=gr.id)
            else:
                new_access.save()
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
            new_access.save()
            return redirect(criminal)
        return render(request, 'access/personal_access_create.html', context={'form': bound_form, 'criminal': criminal})
