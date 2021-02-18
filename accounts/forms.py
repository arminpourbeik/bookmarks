from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    """
    Form for user registration
    """
    password = forms.CharField(label='Password', widget=forms.PasswordInput, )
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput, help_text='Confirm your password')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(
                'Passwords don\'t match.'
            )
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')
