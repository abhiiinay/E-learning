from django.contrib.auth.forms import UserCreationForm
from instructorApp.models import User
from django import forms

class InstructorCreateForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']   # ← ONLY model fields!
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
