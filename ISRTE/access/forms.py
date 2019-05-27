from django import forms
from .models import GroupAccess, PersonAccess, RequestToOpen


class GroupAccessForm(forms.ModelForm):
    class Meta:
        model = GroupAccess
        fields = ['group_id', 'add', 'update', 'execute']
        widgets = {
            'group_id': forms.Select(attrs={'class': 'form-control'})
        }


class GroupAccessUpdateForm(forms.ModelForm):
    class Meta:
        model = GroupAccess
        fields = ['doc_id', 'group_id', 'add', 'update', 'execute']
        widgets = {
            'group_id': forms.Select(attrs={'class': 'form-control'}),
            'doc_id': forms.Select(attrs={'class': 'form-control'})
        }


class PersonalAccessForm(forms.ModelForm):
    class Meta:
        model = PersonAccess
        fields = ['user_id', 'add_access', 'update', 'execute_access', 'special']
        widgets = {
            'user_id': forms.Select(attrs={'class': 'form-control'}),
        }


class PersonalAccessUpdateForm(forms.ModelForm):
    class Meta:
        model = PersonAccess
        fields = ['doc_id', 'user_id', 'add_access', 'update', 'execute_access', 'special']
        widgets = {
            'user_id': forms.Select(attrs={'class': 'form-control'}),
            'doc_id': forms.Select(attrs={'class': 'form-control'})
        }


class RequestToOpenAccessForm(forms.ModelForm):
    class Meta:
        model = RequestToOpen
        fields = ['reason_open']
        widgets = {
            'reason_open': forms.Textarea(attrs={'class': 'form-control'})
        }


class RequestToOpenGroupAccessForm(forms.ModelForm):
    class Meta:
        model = RequestToOpen
        fields = ['group_id', 'reason_open']
        widgets = {
            'reason_open': forms.Textarea(attrs={'class': 'form-control'}),
            'group_id': forms.Select(attrs={'class': 'form-control'})
        }


class RequestToOpenRejectForm(forms.ModelForm):
    class Meta:
        model = RequestToOpen
        fields = ['reason_reject']
        widgets = {
            'reason_reject': forms.Textarea(attrs={'class': 'form-control'})
        }


class RequestToOpenAcceptForm(forms.ModelForm):
    class Meta:
        model = PersonAccess
        fields = ['add_access', 'update', 'execute_access', 'special']


class RequestToOpenGroupAcceptForm(forms.ModelForm):
    class Meta:
        model = GroupAccess
        fields = ['add', 'update', 'execute']