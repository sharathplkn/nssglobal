# authenticate/forms.py
from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, University, College

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect
    )
    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        required=False
    )
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'user_type', 'university', 'college', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['college'].queryset = College.objects.none()

        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['college'].queryset = College.objects.filter(university_id=university_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.university:
            self.fields['college'].queryset = self.instance.university.college_set.order_by('name')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)
