from django import forms
from awb.models import PickupRequest


class PickupRequestForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = [
            'agency',
            'pickup_date',
            'status',
            'remarks',
            'admin_remarks'
        ]
        widgets = {
            'pickup_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-indigo-500'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-indigo-500'
            }),
            'admin_remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-indigo-500'
            }),
            'agency': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'status': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
        }



class PickupStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = [
            'status',
            'admin_remarks'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'admin_remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-indigo-500'
            }),
        }
