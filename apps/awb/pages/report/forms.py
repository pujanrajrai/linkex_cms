from django import forms
from accounts.models import Agency, Company, Country
from datetime import datetime, timedelta

DATE_RANGE_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('this_week', 'This Week'),
    ('last_week', 'Last Week'),
    ('this_month', 'This Month'),
    ('last_month', 'Last Month'),
    ('this_year', 'This Year'),
    ('last_year', 'Last Year'),
    ('custom', 'Custom Range'),
]


class MainFilterForm(forms.Form):
    """Main filter form for all sections"""

    date_range = forms.ChoiceField(
        choices=DATE_RANGE_CHOICES,
        required=False,
        initial='today',
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full p-3'})
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'type': 'date'
        })
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'type': 'date'
        })
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        empty_label="All Companies",
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full p-3'})
    )
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.all(),
        required=False,
        empty_label="All Agencies",
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full p-3'})
    )


class ShipmentFilterForm(forms.Form):
    """Additional filters for shipment section"""

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label="All Countries",
        widget=forms.Select(
            attrs={'class': 'ui selection dropdown search w-full p-3'})
    )
