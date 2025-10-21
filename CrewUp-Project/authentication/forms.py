from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')
    
     def save(self, commit=True):
        """
        Save the provided password in hashed format and capture the email.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user