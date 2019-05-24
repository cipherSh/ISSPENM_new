from django import forms
from .models import GroupAccess, PersonAccess


class GroupAccessForm(forms.ModelForm):
    class Meta:
        model = GroupAccess
        fields = ['group_id', 'add', 'update', 'execute']
        widgets = {
            'group_id': forms.Select(attrs={'class': 'form-control'})
        }


class PersonalAccessForm(forms.ModelForm):
    class Meta:
        model = PersonAccess
        fields = ['user_id', 'add', 'update', 'execute', 'special']
        widgets = {
            'user_id': forms.Select(attrs={'class': 'form-control'}),
        }
