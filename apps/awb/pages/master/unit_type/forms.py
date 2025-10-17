# unit_type/forms.py
from django import forms
from awb.models import UnitType


class UnitTypeForm(forms.ModelForm):
    class Meta:
        model = UnitType
        fields = ['name', 'priority', 'vendor']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'vendor': forms.SelectMultiple(attrs={
                'class': 'ui selection dropdown search w-full'
            })
        }
