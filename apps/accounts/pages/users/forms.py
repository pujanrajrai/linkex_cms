from django import forms
from accounts.models import User
from django.contrib.auth.forms import SetPasswordForm


class UserForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'id': 'id_user_email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'autocomplete': 'current-password'
        }),
        min_length=8
    )

    contact_no = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'contact_no',
            'password',
        ]
        widgets = {

            'full_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
                'autocomplete': 'none'
            })

        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'id': 'id_user_email',
            'autocomplete': 'username'
        })
    )

    contact_no = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'autocomplete': 'none'
        })
    )

    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'contact_no',
        ]
        widgets = {

            'full_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
                'autocomplete': 'off'
            }),
            'contact_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),

        }


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
