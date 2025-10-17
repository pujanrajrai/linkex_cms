from django import forms
from accounts.models import Agency, Company
from django.contrib.auth.decorators import login_required


class LedgerFilterForm(forms.Form):
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.all(),
        empty_label="Select Agency",
        required=False,
        widget=forms.Select(attrs={'class': 'search-input'})
    )

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        empty_label="Select Company",
        required=False,
        widget=forms.Select(attrs={'class': 'search-input'})
    )

    from_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'search-input', 'type': 'date'}),
        required=False
    )

    to_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'search-input', 'type': 'date'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If user is agency user, filter agency choices to only their agency
        if user and user.role == 'agencyuser' and user.agency:
            self.fields['agency'].queryset = Agency.objects.filter(
                id=user.agency.id)
            self.fields['agency'].initial = user.agency
