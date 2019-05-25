import re
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# forms
from .forms import CriminalCreateForm, CriminalContactDetailAddForm, CriminalAddContactPersonForm, \
    CriminalAddAddressForm, PersonsCreateForm, CriminalOwnerChangeForm, CriminalAddRelativeForm, \
    CriminalConfidentChangeForm, CriminalManhuntAddForm, CriminalsCriminalCaseAddForm, CriminalCaseCreateForm, \
    CriminalConvictionAddForm, CriminalManhuntUpdateForm

# models
from .models import Criminals, Persons, CriminalAddresses, Conviction, Confluence, Contacts, Manhunt, CriminalCase, \
    CriminalCaseCriminals, CriminalsContactPersons, CriminalsRelatives

from users.models import Profile
from django.contrib.auth.models import User
from access.models import PersonAccess

# views
from access.views import determinate_owner_or_superuser, assign_full_access, determinate_have_access, access_determinate

# Create your views here.

@login_required
def homepage(request):
    criminal = Criminals.objects.all().count()
    terr = Criminals.objects.filter(occupation=1).count()
    persons = Persons.objects.all().count()
    cp = criminal + persons
    manhunt = Manhunt.objects.all().count()
    case = CriminalCase.objects.all().count()
    mc = manhunt + case
    profile = Profile.objects.all().count()
    active = User.objects.filter(is_active=True).count()
    deactive = profile - active
    context = {
        'criminal': criminal,
        'persons': persons,
        'cp': cp,
        'terr': terr,
        'manhunt': manhunt,
        'case': case,
        'profile': profile,
        'active': active,
        'deactive': deactive,
        'mc': mc
    }
    return render(request, 'home.html', context=context)


@login_required
def registry_page(request):
    nav_btn_add = 'criminal_create_url'
    wrapper_title = "Реестр"
    criminals = Criminals.objects.order_by('-created')[:10]
    my_docs = Criminals.objects.filter(owner=request.user.profile).order_by('-created')[:10]
    if not request.user.is_superuser:
        uncheck_docs = Criminals.objects.filter(owner=request.user.profile).filter(check=False).order_by(
            '-created')[:10]
    else:
        uncheck_docs = Criminals.objects.filter(check=False).order_by(
            '-created')[:10]
    search_url = 'criminals_list_url'

    context = {
        'criminals': criminals,
        'my_docs': my_docs,
        'uncheck_docs': uncheck_docs,
        'nav_btn_add': nav_btn_add,
        'wrapper_title': wrapper_title,
        'recent': True,
        'search_url': search_url
    }
    return render(request, 'reestr/registry_main_page.html', context=context)


@login_required
def criminals_list(request):
    nav_btn_add = 'criminal_create_url'
    wrapper_title = "Реестр"
    search_url = 'criminals_list_url'

    search_query = request.GET.get('search_query_text', '')

    if search_query:
        text = re.split('\W+', search_query)
        for word in text:
            criminals = Criminals.objects.filter(Q(last_name__icontains=word) | Q(first_name__icontains=word) |
                                                 Q(patronymic__icontains=word) | Q(birthday__icontains=word) |
                                                 Q(INN__icontains=word))
    else:
        criminals = Criminals.objects.all()
    context = {
        'criminals': criminals,
        'nav_btn_add': nav_btn_add,
        'wrapper_title': wrapper_title,
        'search_url': search_url
    }
    return render(request, "reestr/criminals/criminals_list.html", context=context)


@login_required
def criminal_detail(request, pk):
    criminal = Criminals.objects.get(id=pk)
    address = CriminalAddresses.objects.filter(criminal_id=criminal)
    contacts_detail = Contacts.objects.filter(criminal_id=criminal)
    relatives = CriminalsRelatives.objects.filter(criminal_id=criminal)
    contact_persons = CriminalsContactPersons.objects.filter(criminal_id=criminal)
    conviction = Conviction.objects.filter(criminal_id=criminal)
    manhunt = Manhunt.objects.filter(criminal_id=criminal)
    criminal_case = CriminalCaseCriminals.objects.filter(criminal_id=criminal)
    pr = PersonAccess.objects.filter(doc_id=criminal).filter(user_id=request.user.profile)
    context = {
        'criminal': criminal,
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': "Реестр",
        'search_url': 'criminals_list_url',
        'address': address,
        'contacts_detail': contacts_detail,
        'relatives': relatives,
        'contact_persons': contact_persons,
        'convictions': conviction,
        'manhunt': manhunt,
        'criminal_case': criminal_case,
        'access': pr
    }
    full_access = determinate_owner_or_superuser(request, criminal)

    if determinate_have_access(request, criminal):
        if full_access:
            request = assign_full_access(request)
        else:
            request = access_determinate(request, criminal)
        return render(request, 'reestr/criminals/criminal_detail.html', context=context)
    return HttpResponse('sorry')




@login_required
def criminal_close_change(request, pk):
    criminal = Criminals.objects.get(id=pk)
    if criminal.close == False:
        criminal.close = True
    else:
        criminal.close = False
    criminal.save()
    return redirect(criminal)


@login_required
def criminal_check(request, pk):
    criminal = Criminals.objects.get(id=pk)
    criminal.check = True
    criminal.save()
    return redirect(criminal)


# Criminal case

@login_required
def cc_list(request):

    search_query = request.GET.get('search_query_text', '')

    if search_query:
        text = re.split('\W+', search_query)
        for word in text:
            cc = CriminalCase.objects.filter(Q(number__icontains=word) | Q(year__icontains=word) |
                                             Q(organ__icontains=word) | Q(date_arousal__icontains=word) | Q(date_suspension__icontains=word))
    else:
        cc = CriminalCase.objects.all()

    context = {
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': "Уголовные дела",
        'search_url': 'cc_list_url',
        'case_list': cc
    }
    return render(request, 'reestr/criminal_case_main_page.html', context=context)


@login_required
def cc_detail(request, pk):
    cc = CriminalCase.objects.get(id=pk)
    ccm = CriminalCaseCriminals.objects.filter(criminal_case=cc)
    context = {
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': "Уголовные дела",
        'search_url': 'cc_list_url',
        'case': cc,
        'ccm': ccm
    }
    return render(request, 'reestr/ccase/cc-detail.html', context=context)


# Manhunt
@login_required
def manhunt_list(request):
    search_query = request.GET.get('search_query_text', '')
    if search_query:
        manhunts = Manhunt.objects.filter(Q(invest_case_number__icontains=search_query) |
                                          Q(date_arousal__icontains=search_query))
    else:
        manhunts = Manhunt.objects.order_by('date_arousal')
    context = {
        'wrapper_title': "Розыскные дела",
        'search_url': 'manhunt_list_url',
        'manhunts': manhunts
    }
    return render(request, 'reestr/manhunt_main_page.html', context=context)


@login_required
def manhunt_detail(request, pk):
    manhunt = Manhunt.objects.get(id=pk)
    context = {
        'wrapper_title': "Розыскные дела",
        'search_url': 'manhunt_list_url',
        'manhunt': manhunt
    }
    return render(request, 'reestr/ccase/manhunt-detail.html', context=context)


class CriminalCreateView(View):
    def get(self, request):
        form = CriminalCreateForm()
        wrapper_title = 'Реестр'
        context = {
            'form': form,
            'wrapper_title': wrapper_title
        }
        return render(request, 'reestr/criminals/criminal_create.html', context=context)

    def post(self, request):
        bound_form = CriminalCreateForm(request.POST)

        if bound_form.is_valid():
            new_criminal = bound_form.save(commit=False)
            new_criminal.user = request.user.profile
            new_criminal.owner = request.user.profile
            new_criminal.full_name = new_criminal.last_name + ' ' + new_criminal.first_name + ' ' + \
                                     new_criminal.patronymic
            new_criminal.save()
            return redirect(new_criminal)
        return render(request, 'persons/criminal_create.html', context={'form': bound_form})


class CriminalUpdateView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalCreateForm(instance=criminal)
        context = {
            'form': bound_form,
            'criminal': criminal,
            'wrapper_title': 'Реестр'
        }
        return render(request, 'reestr/criminals/criminal_update.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalCreateForm(request.POST, instance=criminal)
        context = {
            'form': bound_form,
            'criminal': criminal,
            'wrapper_title': 'Реестр'
        }
        if bound_form.is_valid():
            new_criminal = bound_form.save()
            return redirect(new_criminal)
        return render(request, 'reestr/criminals/criminal_update.html', context=context)


class CriminalDeleteView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        context = {
            'criminal': criminal,
            'wrapper_title': 'Реестр',
        }
        return render(request, 'reestr/criminals/criminal_delete.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        criminal.delete()
        return redirect(reverse('criminals_list_url'))


class CriminalContactDetailAddView(View):
    def get(self, request, pk):
        form = CriminalContactDetailAddForm()
        criminal = Criminals.objects.get(id=pk)
        return render(request, 'reestr/criminals/add/criminal_contact_add.html', context={'form': form, 'criminal': criminal})

    def post(self, request, pk):
        bound_form = CriminalContactDetailAddForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_form.is_valid():
            new_contact = bound_form.save(commit=False)
            new_contact.criminal_id = criminal
            new_contact.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_contact_add.html',
                      context={'form': bound_form, 'criminal': criminal})


class CriminalAddAddressView(View):
    def get(self, request, pk):
        form = CriminalAddAddressForm()
        criminal = Criminals.objects.get(id=pk)
        return render(request, 'reestr/criminals/add/criminal_add_address.html', context={'form': form, 'criminal': criminal})

    def post(self, request, pk):
        bound_form = CriminalAddAddressForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_form.is_valid():
            new_address = bound_form.save(commit=False)
            new_address.criminal_id = criminal
            new_address.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_add_address.html', context={'form': bound_form,
                                                                                 'criminal': criminal})


class CriminalAddRelativeView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        person_form = PersonsCreateForm()
        add_form = CriminalAddRelativeForm()
        return render(request, 'reestr/criminals/add/criminal_add_relative.html', context={'person_form': person_form,
                                                                                  'add_form': add_form,
                                                                                  'criminal': criminal})

    def post(self, request, pk):
        bound_add_form = CriminalAddRelativeForm(request.POST)
        bound_person_form = PersonsCreateForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_add_form.is_valid() and bound_person_form.is_valid():
            new_person = bound_person_form.save(commit=False)
            new_person.user = request.user.profile
            new_person.save()
            new_add = bound_add_form.save(commit=False)
            new_add.criminal_id = criminal
            new_add.person_id = new_person
            new_add.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_add_relative.html', context={'person_form': bound_person_form,
                                                                                  'add_form': bound_add_form,
                                                                                  'criminal': criminal})


class CriminalAddContactPersonView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        person_form = PersonsCreateForm()
        add_form = CriminalAddContactPersonForm()
        return render(request, 'reestr/criminals/add/criminal_add_contact-person.html', context={'person_form': person_form,
                                                                                        'add_form': add_form,
                                                                                        'criminal': criminal})

    def post(self, request, pk):
        bound_add_form = CriminalAddContactPersonForm(request.POST)
        bound_person_form = PersonsCreateForm(request.POST)
        criminal = Criminals.objects.get(id=pk)

        if bound_add_form.is_valid() and bound_person_form.is_valid():
            new_person = bound_person_form.save(commit=False)
            new_person.user = request.user.profile
            new_person.save()
            new_add = bound_add_form.save(commit=False)
            new_add.criminal_id = criminal
            new_add.person_id = new_person
            new_add.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_add_contact-person.html',
                      context={'person_form': bound_person_form,
                               'add_form': bound_add_form,
                               'criminal': criminal})


class CriminalOwnerChangeView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalOwnerChangeForm(instance=criminal)
        return render(request, 'reestr/criminals/add/criminal_owner_change.html', context={'form': bound_form,
                                                                                  'criminal': criminal})

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalOwnerChangeForm(request.POST, instance=criminal)
        if bound_form.is_valid():
            bound_form.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_owner_change.html', context={'form': bound_form,
                                                                                  'criminal': criminal})


class CriminalConfidentChangeView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalConfidentChangeForm(instance=criminal)
        return render(request, 'reestr/criminals/add/criminal_confident_change.html', context={'form': bound_form,
                                                                                      'criminal': criminal})

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalConfidentChangeForm(request.POST, instance=criminal)
        if bound_form.is_valid():
            bound_form.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_confident_change.html', context={'form': bound_form,
                                                                                      'criminal': criminal})


class CriminalConvictionAddView(View):
    def get(self, request, pk):
        form = CriminalConvictionAddForm()
        criminal = Criminals.objects.get(id=pk)
        context = {
            'criminal': criminal,
            'form': form,
        }
        return render(request, 'reestr/criminals/add/conviction_add.html', context=context)

    def post(self, request, pk):
        bound_form = CriminalConvictionAddForm(request.POST)
        criminal = Criminals.objects.get(id=pk)
        context = {
            'criminal': criminal,
            'form': bound_form,
        }

        if bound_form.is_valid():
            new_conviction = bound_form.save(commit=False)
            new_conviction.criminal_id = criminal
            new_conviction.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/conviction_add.html', context=context)


class CriminalCriminalCaseAddView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        case_form = CriminalCaseCreateForm()
        case_add_form = CriminalsCriminalCaseAddForm()
        context = {
            'criminal': criminal,
            'case_form': case_form,
            'case_add_form': case_add_form
        }
        return render(request, 'reestr/criminals/add/criminal_case_add.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_case_form = CriminalCaseCreateForm(request.POST)
        bound_case_add_form = CriminalsCriminalCaseAddForm(request.POST)
        context = {
            'criminal': criminal,
            'case_form': bound_case_form,
            'case_add_form': bound_case_add_form
        }

        if bound_case_form.is_valid() and bound_case_add_form.is_valid():
            new_case = bound_case_form.save()
            new_add_case = bound_case_add_form.save(commit=False)
            new_add_case.criminal_id = criminal
            new_add_case.criminal_case = new_case
            new_add_case.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_case_add.html', context=context)


class CriminalManhuntAddView(View):
    def get(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        form = CriminalManhuntAddForm()

        context = {
            'criminal': criminal,
            'form': form,
        }
        return render(request, 'reestr/criminals/add/manhunt_add.html', context=context)

    def post(self, request, pk):
        criminal = Criminals.objects.get(id=pk)
        bound_form = CriminalManhuntAddForm(request.POST)
        context = {
            'criminal': criminal,
            'form': bound_form,
        }
        if bound_form.is_valid():
            new_manhunt = bound_form.save(commit=False)
            new_manhunt.criminal_id = criminal
            new_manhunt.save()
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/manhunt_add.html', context=context)


class ManhuntUpdateView(View):
    def get(self, request, pk):
        manhunt = Manhunt.objects.get(id=pk)
        form = CriminalManhuntUpdateForm(instance=manhunt)

        context = {
            'manhunt': manhunt,
            'form': form,
        }
        return render(request, 'reestr/ccase/manhunt_update.html', context=context)

    def post(self, request, pk):
        manhunt = Manhunt.objects.get(id=pk)
        bound_form = CriminalManhuntUpdateForm(request.POST)
        context = {
            'manhunt': manhunt,
            'form': bound_form,
        }
        if bound_form.is_valid():
            new_manhunt = bound_form.save()
            return redirect(new_manhunt)
        return render(request, 'reestr/ccase/manhunt_update.html', context=context)


class ManhuntDeleteView(View):
    def get(self, request, pk):
        manhunt = Manhunt.objects.get(id=pk)
        context = {
            'manhunt': manhunt,
            'wrapper_title': 'Розыскное дело',
        }
        return render(request, 'reestr/criminals/criminal_delete.html', context=context)

    def post(self, request, pk):
        manhunt = Manhunt.objects.get(id=pk)
        manhunt.delete()
        return redirect(reverse('manhunt_list_url'))
