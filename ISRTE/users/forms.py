from django import forms

from .models import Profile, UserLogs
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role_id', 'trust_level_id']

        widgets = {
            'role_id': forms.Select(attrs={'class': 'form-control'}),
            'trust_level_id': forms.Select(attrs={'class': 'form-control'}),
        }


class UserLogsSearchForm(forms.ModelForm):
    class Meta:
        model = UserLogs
        fields = ['user']

        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
        }