from django import forms
from finance.models import Invoice
from awb.models.awb import AWBDetail


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'total_weight',
            'total_box',
            'per_box_handling_fee',
            'per_kg_customs_fee',
            'total_amount',
            'grand_total',
            'total_paid_amount',
            'payment_method',
            'remark',
            'document'
        ]
        widgets = {
            'total_weight': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01'}),
            'total_box': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'min': '1'}),
            'per_box_handling_fee': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01'}),
            'per_kg_customs_fee': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01'}),
            'grand_total': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-gray-100 px-3 text-gray-600 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01', 'readonly': True}),
            'total_paid_amount': forms.NumberInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'remark': forms.Textarea(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'rows': 3}),
            'document': forms.FileInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
        }

    def __init__(self, *args, **kwargs):
        awb = kwargs.pop('awb', None)
        super().__init__(*args, **kwargs)

        if awb:
            # Pre-populate values from AWB and Agency
            awb_detail = AWBDetail.objects.get(awbno=awb.awbno)
            agency = awb_detail.agency
            # Set default values from AWB
            self.fields['total_weight'].initial = awb_detail.total_charged_weight or 0
            self.fields['total_box'].initial = awb_detail.total_box or 1

            # Set default values from Agency if available
            if agency:
                self.fields['per_box_handling_fee'].initial = agency.handling_per_box_rate or 0
                self.fields['per_kg_customs_fee'].initial = agency.custom_per_kg_rate or 0
            else:
                self.fields['per_box_handling_fee'].initial = 0
                self.fields['per_kg_customs_fee'].initial = 0
