from django import forms
from .models import Criminals, Persons, CriminalsRelatives, CriminalsContactPersons, CriminalAddresses, Contacts, \
    Conviction, CriminalCase, CriminalCaseCriminals, Manhunt


class CriminalCreateForm(forms.ModelForm):
    class Meta:
        model = Criminals
        fields = ['first_name', 'last_name', 'patronymic', 'birthday', 'birth_country', 'birth_region',
                  'birth_District', 'birth_City', 'birth_Village', 'gender', 'citizenship', 'INN', 'passport_serial',
                  'passport_number', 'issue_organ', 'issue_data', 'education', 'education_place', 'profession',
                  'marital_status', 'occupation', 'status', 'image', 'organization', 'remarks', 'close', 'confident']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control'}),
            'confident': forms.Select(attrs={'class': 'form-control'})
        }


class PersonsCreateForm(forms.ModelForm):
    class Meta:
        model = Persons
        fields = ['first_name', 'last_name', 'patronymic', 'birthday', 'birth_country', 'birth_region',
                  'birth_District', 'birth_City', 'birth_Village', 'gender', 'citizenship', 'INN', 'passport_serial',
                  'passport_number', 'issue_organ', 'issue_data', 'education', 'education_place', 'profession',
                  'job', 'workplace', 'marital_status', 'phone', 'email', 'status', 'image', 'remarks']


class CriminalAddRelativeForm(forms.ModelForm):
    class Meta:
        model = CriminalsRelatives
        fields = ['relation']


class CriminalAddContactPersonForm(forms.ModelForm):
    class Meta:
        model = CriminalsContactPersons
        fields = ['relation']


class CriminalAddAddressForm(forms.ModelForm):
    class Meta:
        model = CriminalAddresses
        fields = ['kind', 'region', 'district', 'city', 'village', 'micro_district', 'street', 'home', 'date_entry',
                  'date_release', 'remarks']


class CriminalContactDetailAddForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['type_contact', 'contact', 'remarks']


class CriminalOwnerChangeForm(forms.ModelForm):
    class Meta:
        model = Criminals
        fields = ['owner']


class CriminalConfidentChangeForm(forms.ModelForm):
    class Meta:
        model = Criminals
        fields = ['confident']


class CriminalCaseCreateForm(forms.ModelForm):
    class Meta:
        model = CriminalCase
        fields = ['number', 'year', 'article', 'organ', 'date_arousal', 'date_suspension', 'remarks']


class CriminalsCriminalCaseAddForm(forms.ModelForm):
    class Meta:
        model = CriminalCaseCriminals
        fields = []


class CriminalManhuntAddForm(forms.ModelForm):
    class Meta:
        model = Manhunt
        fields = ['invest_case_number', 'criminalCase_id', 'date_arousal', 'invest_initiator', 'invest_category',
                  'circular_number', 'preventive', 'date_inter_invest', 'invest_stopped', 'place_detention',
                  'date_detention', 'invest_stopped_circular']


class CriminalManhuntUpdateForm(forms.ModelForm):
    class Meta:
        model = Manhunt
        fields = ['invest_case_number', 'criminal_id', 'criminalCase_id', 'date_arousal', 'invest_initiator', 'invest_category',
                  'circular_number', 'preventive', 'date_inter_invest', 'invest_stopped', 'place_detention',
                  'date_detention', 'invest_stopped_circular']


class CriminalConvictionAddForm(forms.ModelForm):
    class Meta:
        model = Conviction
        fields = ['criminal_case_number', 'criminal_case_year', 'criminal_case_organ', 'law_article', 'date_sentence',
                  'date_release']
