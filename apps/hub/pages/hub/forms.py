from django import forms
from hub.models import Hub
from accounts.models import Country


class HubForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        label='C O U N T R Y',
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={
            'class': 'ui selection dropdown search w-full p-3',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Hub
        fields = ['name', 'hub_code', 'country',
                  'city', 'currency', 'vendor',
                  'priority'

                  ]
        widgets = {
            "name": forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            "hub_code": forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            "currency": forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            "manifest_format": forms.SelectMultiple(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            "country": forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            "city": forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            "vendor": forms.SelectMultiple(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            "rate_currency": forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
        }



class UploadHubRateForm(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'accept': '.csv, .xlsx, .xls'
        })
    )

