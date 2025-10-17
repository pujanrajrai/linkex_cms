from django import forms
from finance.models import Ledger
from accounts.models import Agency, Company
from finance.models.ledger import ledger_type


class LedgerForm(forms.Form):
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.filter(is_blocked=False),
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full'})
    )
    ledger_type = forms.ChoiceField(choices=ledger_type,
                                    widget=forms.Select(
                                        attrs={'class': 'ui selection dropdown search w-full'})
                                    )
    particular = forms.CharField(max_length=255,
                                 widget=forms.TextInput(
                                     attrs={'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'})
                                 )
    amount = forms.FloatField(
        widget=forms.TextInput(
            attrs={'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'})
    )

    remarks = forms.CharField(max_length=255,
                              widget=forms.TextInput(
                                  attrs={'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'})
                              )
