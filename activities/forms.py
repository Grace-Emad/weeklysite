from django import forms
from django.contrib.auth.models import User

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'week_date', 'start_time', 'end_time', 'max_participants', 'points']
        widgets = {
            'week_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AccountCreateForm(forms.Form):
    """Used by an admin to create a brand new account for someone."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    is_staff = forms.BooleanField(
        required=False,
        label="Give this account admin access",
        help_text="Admins can create activities, accounts, and manage enrollments.",
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username


class AccountEditForm(forms.Form):
    """Used by an admin to edit an existing account's score and admin access."""
    score = forms.IntegerField()
    is_staff = forms.BooleanField(required=False, label="Give this account admin access")