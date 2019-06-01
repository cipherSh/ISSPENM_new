import re
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# forms
from .forms import CriminalCreateForm, CriminalContactDetailAddForm, CriminalAddContactPersonForm, \
    CriminalAddAddressForm, PersonsCreateForm, CriminalOwnerChangeForm, CriminalAddRelativeForm, \
    CriminalConfidentChangeForm, CriminalManhuntAddForm, CriminalsCriminalCaseAddForm, CriminalCaseCreateForm, \
    CriminalConvictionAddForm, CriminalManhuntUpdateForm, CriminalCaseUpdateForm,AddExistingCriminalForm

# models
from .models import Criminals, Persons, CriminalAddresses, Conviction, Confluence, Contacts, Manhunt, CriminalCase, \
    CriminalCaseCriminals, CriminalsContactPersons, CriminalsRelatives, Occupation

from users.models import Profile, Role
from django.contrib.auth.models import User
from access.models import PersonAccess, RequestToOpen

# views
from access.views import determinate_owner_or_superuser, assign_full_access, determinate_have_access, access_determinate
from users.views import action_logging_create, action_logging_view, action_logging_update, action_logging_delete, \
    action_logging_added, action_logging_exclude, action_logging_other, object_logs

# Create your views here.


@login_required
def homepage(request):
    count_criminals = Criminals.objects.all().count()
    mto = Occupation.objects.get(type_occ='МТО')
    meo = Occupation.objects.get(type_occ='МЭО')
    count_terror = Criminals.objects.filter(occupation=mto).count()
    count_extrem = Criminals.objects.filter(occupation=meo).count()
    count_persons = Persons.objects.all().count()
    count_cc = CriminalCase.objects.all().count()
    count_manhunt = Manhunt.objects.all().count()
    count_active_users = User.objects.filter(is_active=True).count()
    count_inactive_users = User.objects.filter(is_active=False).count()

    search_query = request.GET.get('text', '')

    criminals = None
    cc = None
    manhunts = None
    profiles = None
    users = None
    roles = None

    if search_query:
        text = re.split('\W+', search_query)
        for word in text:
            criminals = Criminals.objects.filter(Q(last_name__icontains=word) | Q(first_name__icontains=word) |
                                                 Q(patronymic__icontains=word) | Q(birthday__icontains=word) |
                                                 Q(INN=word))
            cc = CriminalCase.objects.filter(Q(number__icontains=word) | Q(year__icontains=word) |
                                             Q(organ__icontains=word) | Q(date_arousal__icontains=word) | Q(
                                                                            date_suspension__icontains=word))
            manhunts = Manhunt.objects.filter(Q(invest_case_number__icontains=word) |
                                              Q(date_arousal__icontains=word) |
                                              Q(invest_initiator__icontains=word))
            if word == 'admin' or word == 'head':
                roles = Role.objects.get(role_type=word)
            if roles:
                profiles = Profile.objects.filter(role_id=roles)
            users = User.objects.filter(Q(last_name__icontains=word) | Q(first_name__icontains=word) | Q(
                username__icontains=word))
    my_requests = RequestToOpen.objects.filter(user_id=request.user.profile).filter(check=True).order_by('-date_check')

    context = {
        'count_criminals': count_criminals,
        'count_terror': count_terror,
        'count_extrem': count_extrem,
        'count_persons': count_persons,
        'count_cc': count_cc,
        'count_manhunt': count_manhunt,
        'count_active_users': count_active_users,
        'count_inactive_users': count_inactive_users,
        'criminals': criminals,
        'ccase': cc,
        'manhunts': manhunts,
        'profiles': profiles,
        'users': users,
        'search_text': search_query,
        'my_requests': my_requests,

    }
    return render(request, 'home.html', context=context)


@login_required
def registry_page(request):
    nav_btn_add = 'criminal_create_url'
    wrapper_title = "Реестр"
    criminals = Criminals.objects.order_by('-created')[:50]
    docs_requests = []
    docs_requests_group = []


    search_url = 'criminals_list_url'

    context = {
        'criminals': criminals,
        'uncheck_docs': uncheck_docs,
        'docs_requests': docs_requests,
        'docs_requests_group': docs_requests_group,
        'nav_btn_add': nav_btn_add,
        'wrapper_title': wrapper_title,
        'recent': True,
        'search_url': search_url
    }
    return render(request, 'reestr/registry_main_page.html', context=context)


@login_required
def my_doc(request):
    my_docs = Criminals.objects.filter(owner=request.user.profile).order_by('-created')[:10]
    context = {
        'my_docs': my_docs,
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': 'Реестр',
        'recent': True,
        'search_url': 'criminals_list_url'
    }
    return render(request, 'reestr/registry_main_page.html', context=context)


@login_required
def uncheck_docs(request):
    uncheck_docs = None
    if not request.user.is_superuser:
        uncheck_docs = Criminals.objects.filter(owner=request.user.profile).filter(check=False).order_by(
            '-created')[:10]
    else:
        uncheck_docs = Criminals.objects.filter(check=False).order_by(
            '-created')[:10]
    context = {
        'uncheck_docs': uncheck_docs,
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': 'Реестр',
        'recent': True,
        'search_url': 'criminals_list_url'
    }
    return render(request, 'reestr/registry_main_page.html', context=context)


@login_required
def qq_list(request):
    docs_requests = None
    docs_requests_group = None
    my_docs = Criminals.objects.filter(owner=request.user.profile).order_by('-created')[:10]
    for my_doc in my_docs:
        docs_requests = RequestToOpen.objects.filter(doc=my_doc).filter(group_id=None).filter(check=False).order_by(
            '-date_request')[:10]
        docs_requests_group = RequestToOpen.objects.filter(doc=my_doc).filter(group_id=not None).filter(
            check=False).order_by('-date_request')[:10]
    context = {
        'docs_requests': docs_requests,
        'docs_requests_group': docs_requests_group,
        'nav_btn_add': 'criminal_create_url',
        'wrapper_title': 'Реестр',
        'recent': True,
        'search_url': 'criminals_list_url'
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
    similar = similar_criminal(request, criminal)
    context = {
        'criminal': criminal,
        'similar': similar,
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
        action_logging_view(request, criminal)
        return render(request, 'reestr/criminals/criminal_detail.html', context=context)
    return render(request, 'reestr/criminals/request_to_open_access.html', context=context)


@login_required
def criminal_logs(request, pk):
    criminal = Criminals.objects.get(id=pk)
    logs = object_logs(request, criminal)
    context = {
        'criminal': criminal,
        'logs': logs,
        'wrapper_title': 'Реестр'
    }
    return render(request, 'reestr/logs/criminal_logs.html', context=context)


def similar_criminal(request, criminal):
    similar = Criminals.objects.filter(INN__icontains=criminal.INN)
    print(similar)
    temp = []
    for sim in similar:
        if not sim == criminal:
            temp.append(sim)
    similar = temp
    mans = []
    contacts_detail = None
    address = None
    relatives = None
    contact_persons = None
    conviction = None
    manhunt = None
    criminal_case = None
    for sim in similar:
        address = CriminalAddresses.objects.filter(criminal_id=sim)
        contacts_detail = Contacts.objects.filter(criminal_id=sim)
        relatives = CriminalsRelatives.objects.filter(criminal_id=sim)
        contact_persons = CriminalsContactPersons.objects.filter(criminal_id=sim)
        conviction = Conviction.objects.filter(criminal_id=sim)
        manhunt = Manhunt.objects.filter(criminal_id=sim)
        criminal_case = CriminalCaseCriminals.objects.filter(criminal_id=sim)
        temp = {
            'man': sim,
            'contacts_detail': contacts_detail,
            'address': address,
            'relatives': relatives,
            'contact_persons': contact_persons,
            'conviction': conviction,
            'manhunt': manhunt,
            'criminal_case': criminal_case,
        }
        mans.append(temp)
    return mans


@login_required
def criminal_close_change(request, pk):
    log_message = {'message': ''}
    criminal = Criminals.objects.get(id=pk)
    if criminal.close:
        criminal.close = False
        log_message = {'message': 'Закрыл доступ'}
    else:
        criminal.close = True
        log_message = {'message': 'Открыл доступ'}
    criminal.save()
    action_logging_other(request, criminal, message=log_message)
    return redirect(criminal)


@login_required
def criminal_check(request, pk):
    criminal = Criminals.objects.get(id=pk)
    criminal.check = True
    criminal.save()
    log_message = {'message': 'Подтвердил'}
    action_logging_other(request, criminal, message=log_message)
    return redirect(criminal)


# Criminal case

@login_required
def cc_list(request):

    search_query = request.GET.get('search_query_text', '')

    if search_query:
        text = re.split('\W+', search_query)
        for word in text:
            cc = CriminalCase.objects.filter(Q(number__icontains=word) | Q(year__icontains=word) |
                                             Q(organ__icontains=word) | Q(date_arousal__icontains=word) |
                                             Q(date_suspension__icontains=word))
    else:
        cc = CriminalCase.objects.all()

    context = {
        'nav_btn_add': 'cc_create_url',
        'wrapper_title': "Уголовные дела",
        'search_url': 'cc_list_url',
        'case_list': cc
    }
    return render(request, 'reestr/criminal_case_main_page.html', context=context)


@login_required
def cc_detail(request, pk):
    cc = CriminalCase.objects.get(id=pk)
    ccm = CriminalCaseCriminals.objects.filter(criminal_case=cc)
    form = AddExistingCriminalForm()
    delete = None
    action_logging_view(request, cc)
    context = {
        'nav_btn_add': 'cc_create_url',
        'wrapper_title': "Уголовные дела",
        'search_url': 'cc_list_url',
        'form': form,
        'delete': delete,
        'case': cc,
        'ccm': ccm
    }
    return render(request, 'reestr/ccase/cc-detail.html', context=context)


@login_required
def cc_logs(request, pk):
    cc = CriminalCase.objects.get(id=pk)
    logs = object_logs(request, cc)
    context = {
        'cc': cc,
        'logs': logs,
        'wrapper_title': 'Уголовные дела'
    }
    return render(request, 'reestr/logs/criminal_logs.html', context=context)


def cc_criminal_delete(request, pk):
    member = CriminalCaseCriminals.objects.get(id=pk)
    cc = member.criminal_case
    member.delete()
    action_logging_exclude(request, cc, member)
    return redirect(cc)


def add_existing_criminal_to_cc(request, pk):
    cc = CriminalCase.objects.get(id=pk)
    if request.POST:
        bound_form = AddExistingCriminalForm(request.POST)
        if bound_form.is_valid():
            new_case = bound_form.save(commit=False)
            new_case.criminal_case = cc
            if CriminalCaseCriminals.objects.filter(criminal_case=new_case.criminal_case).filter(
                    criminal_id=new_case.criminal_id):
                return redirect(cc)
            else:
                action_logging_added(request, cc, new_case.criminal_id)
                new_case.save()
            return redirect(cc)
        return redirect(cc)
    return redirect(cc)


class AddNewCriminalToCCView(View):
    def get(self, request, pk):
        case = CriminalCase.objects.get(id=pk)
        form_criminal = CriminalCreateForm()
        form_add = CriminalsCriminalCaseAddForm()
        context = {
            'case': case,
            'form_criminal': form_criminal,
            'form_add': form_add
        }
        return render(request, 'reestr/ccase/cc_add_criminal.html', context=context)

    def post(self, request, pk):
        case = CriminalCase.objects.get(id=pk)
        bound_form_criminal = CriminalCreateForm(request.POST)
        bound_form_add = CriminalsCriminalCaseAddForm(request.POST)

        if bound_form_criminal.is_valid() and bound_form_add.is_valid():
            new_criminal = bound_form_criminal.save(commit=False)
            new_criminal.owner = request.user.profile
            new_criminal.user = request.user.profile
            new_criminal.save()
            new_case_member = bound_form_add.save(commit=False)
            new_case_member.criminal_case = case
            new_case_member.criminal_id = new_criminal
            new_case_member.save()
            action_logging_create(request, new_criminal)
            action_logging_added(request, case, new_criminal)
            return redirect(case)

        context = {
            'case': case,
            'form_criminal': bound_form_criminal,
            'form_add': bound_form_add
        }
        return render(request, 'reestr/ccase/cc_add_criminal.html', context=context)


# Manhunt
@login_required
def manhunt_list(request):
    search_query = request.GET.get('search_query_text', '')
    if search_query:
        manhunts = Manhunt.objects.filter(Q(invest_case_number__icontains=search_query) |
                                          Q(date_arousal__icontains=search_query) |
                                          Q(invest_initiator__icontains=search_query))
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
    action_logging_view(request, manhunt)
    context = {
        'wrapper_title': "Розыскные дела",
        'search_url': 'manhunt_list_url',
        'manhunt': manhunt
    }
    return render(request, 'reestr/ccase/manhunt-detail.html', context=context)


@login_required
def manhunt_logs(request, pk):
    manhunt = Manhunt.objects.get(id=pk)
    logs = object_logs(request, manhunt)
    context = {
        'cc': manhunt,
        'logs': logs,
        'wrapper_title': 'Уголовные дела'
    }
    return render(request, 'reestr/logs/criminal_logs.html', context=context)



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
            action_logging_create(request, new_criminal)
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
            action_logging_update(request, criminal)
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
        action_logging_delete(request, criminal)
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
            action_logging_create(request, new_contact)
            action_logging_added(request, criminal, new_contact)
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_contact_add.html',
                      context={'form': bound_form, 'criminal': criminal})


def contacts_detail_delete(request, pk):
    contact = Contacts.objects.get(id=pk)
    criminal = contact.criminal_id
    action_logging_exclude(request, criminal, contact)
    action_logging_delete(request, contact)
    contact.delete()
    return redirect(criminal)



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
            action_logging_create(request, new_address)
            action_logging_added(request, criminal, new_address)
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
            action_logging_create(request, new_person)
            action_logging_added(request, criminal, new_person)
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
            action_logging_create(request, new_person)
            action_logging_added(request, criminal, new_person)
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
            new_criminal = bound_form.save()
            log_message = {'message': 'Сменил владельца на {}'.format(new_criminal.owner)}
            action_logging_other(request, criminal, log_message)
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
            updated_criminal = bound_form.save()
            log_message = {'message': 'Сменил метку доступа на {}'.format(updated_criminal.confident)}
            action_logging_other(request, criminal, log_message)
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
            action_logging_create(request, new_conviction)
            action_logging_added(request, criminal, new_conviction)
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
            action_logging_create(request, new_case)
            action_logging_added(request, criminal, new_case)
            return redirect(criminal)
        return render(request, 'reestr/criminals/add/criminal_case_add.html', context=context)


class CriminalCaseCreateView(View):
    def get(self, request):
        form = CriminalCaseCreateForm()
        context = {
            'form': form,
            'wrapper_title': 'Добавить уголовного дела'
        }
        return render(request, 'reestr/ccase/cc_create.html', context=context)

    def post(self, request):
        bound_form = CriminalCaseCreateForm(request.POST)
        error_messages = None
        if bound_form.is_valid():
            new_case = bound_form.save(commit=False)
            if CriminalCase.objects.filter(number=new_case.number).filter(year=new_case.year).count():
                error_messages = 'Дело с номером {} уже зарегистрировано в системе'.format(
                    new_case.number + '/' + new_case.year)
                context = {
                    'form': bound_form,
                    'wrapper_title': 'Добавить уголовного дела',
                    'error_messages': error_messages
                }
                return render(request, 'reestr/ccase/cc_create.html', context=context)
            action_logging_create(request, new_case)
            return redirect(new_case)
        context = {
            'form': bound_form,
            'wrapper_title': 'Добавить уголовного дела'
        }
        return render(request, 'reestr/ccase/cc_create.html', context=context)


class CriminalCaseUpdateView(View):
    def get(self, request, pk):
        cc = CriminalCase.objects.get(id=pk)
        form = CriminalCaseUpdateForm(instance=cc)
        context = {
            'cc': cc,
            'form': form
        }
        return render(request, 'reestr/ccase/cc_update.html', context=context)

    def post(self, request, pk):
        cc = CriminalCase.objects.get(id=pk)
        bound_form = CriminalCaseUpdateForm(request.POST, instance=cc)
        context = {
            'cc': cc,
            'form': bound_form
        }

        if bound_form.is_valid():
            new_case = bound_form.save(commit=False)
            new_case.save()
            action_logging_update(request, cc)
            return redirect(new_case)
        return render(request, 'reestr/ccase/cc_update.html', context=context)


def criminal_case_delete(request, pk):
    cc = CriminalCase.objects.get(id=pk)
    action_logging_delete(request, cc)
    cc.delete()
    return redirect(reverse('cc_list_url'))


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
            action_logging_create(request, new_manhunt)
            action_logging_added(request, criminal, new_manhunt)
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
        bound_form = CriminalManhuntUpdateForm(request.POST, instance=manhunt)
        context = {
            'manhunt': manhunt,
            'form': bound_form,
        }
        if bound_form.is_valid():
            new_manhunt = bound_form.save()
            action_logging_update(request, manhunt)
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
        action_logging_delete(request, manhunt)
        manhunt.delete()
        return redirect(reverse('manhunt_list_url'))
