from django import forms
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-md',
            'placeholder': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full p-3 border border-gray-300 rounded-md',
            'placeholder': 'Password'
        })
    )
    # Use the custom widget for the captcha field
    captcha = CaptchaField()
