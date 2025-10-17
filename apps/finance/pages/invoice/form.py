from django import forms

from finance.models import Invoice
from awb.models import AWBDetail


class InvoiceForm(forms.ModelForm):
    paid_amount = forms.FloatField(
        required=True,
        label='Paid Amount',
        widget=forms.NumberInput(attrs={'autocomplete': 'new-password',
                                 'class': 'text-sm pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'})
    )

    class Meta:
        model = Invoice
        fields = [
            'awb',
            'total_amount',
            'per_box_handling_fee',
            'per_kg_customs_fee',
            'grand_total',
            'total_paid_amount',
            'payment_method',
            'remark',
            'document'
        ]

    def __init__(self, *args, **kwargs):
        awb_no = kwargs.pop('awb_no', None)
        super().__init__(*args, **kwargs)
        if awb_no:
            self.fields['awb'].queryset = AWBDetail.objects.filter(
                awbno=awb_no)
