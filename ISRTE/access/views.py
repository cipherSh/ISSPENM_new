from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import GroupAccessForm, PersonalAccessForm


from .models import PersonAccess, GroupAccess
from reestr.models import Criminals

# Create your views here.

def access_determinate(request, pk):
    doc = Criminals.objects.get(id=pk)

    if not request.user.is_superuser:
        if not doc.owner == request.user.profile:
            request.user.user_permission_add('add_criminals1')
        pa = PersonAccess.objects.filter(user_id=request.user.profile)


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
