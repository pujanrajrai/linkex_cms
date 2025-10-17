from accounts.models.company import Company
from awb.models.masters import ProductType, Service
from awb.models.awb import AWBStatus
from django import forms
from django.db.models.base import Model
from accounts.models.masters import DividingFactor
from awb.models import AWBDetail, Consignee, Consignor, BoxDetails, BoxItem, Currency
from hub.models.hub import Hub
from accounts.models import Country
from hub.models import Vendor
from accounts.models import Agency


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.factor


class VendorModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if self.user and self.user.role == 'admin':
            return f"{obj.name} ({obj.account_number})"
        else:
            return f"{obj.account_number}"


class AWBForm(forms.ModelForm):
    is_custom = forms.BooleanField(
        label="Custom AWB Number",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'text-sm pt-1 pb-1 form-checkbox h-5 w-5 text-gray-600 rounded border-gray-300 focus:ring-gray-500',
            }
        )
    )
    awbno = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'autocomplete': 'off'
        })
    )
    dividing_factor = CustomModelChoiceField(
        queryset=DividingFactor.objects.all(),
        widget=forms.Select(attrs={
            "id": "box_total_dividing_factor",
            "class": "pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 rounded-md",
            "required": True
        }),
        required=True,
        initial=DividingFactor.objects.get(factor=5000) if DividingFactor.objects.filter(
            factor=5000).exists() else DividingFactor.objects.first()
    )
    is_cash_user = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'text-sm pt-1 pb-1 form-checkbox h-5 w-5 text-gray-600 rounded border-gray-300 focus:ring-gray-500'
        })
    )
    hub = forms.ModelChoiceField(
        queryset=Hub.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'autocomplete': 'new-password',
            'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'
        })
    )
    company = forms.ModelChoiceField(
        label="C O M P A N Y",
        queryset=Company.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'autocomplete': 'none',
            'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full',
        })
    )

    vendor = VendorModelChoiceField(
        queryset=Vendor.objects.none(),
        user=None,
        required=False,
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
    )

    product_type = forms.ModelChoiceField(
        required=False,
        queryset=ProductType.objects.none(),
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
    )
    service = forms.ModelChoiceField(
        required=False,
        queryset=Service.objects.none(),
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
    )

    class Meta:
        model = AWBDetail
        fields = ['is_cash_user', 'is_custom', 'awbno',  'agency', 'company', 'hub', 'vendor', 'origin', 'destination', 'product_type', 'service', 'shipment_value', 'currency', 'content',
                  'forwarding_number', 'reference_number',   'dividing_factor', 'reason_for_export', 'incoterms', 'shipment_terms']
        widgets = {
            'agency': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full py-0'}),
            'company': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm pt-1 pb-1 ui selection dropdown search w-full'}),
            'hub': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm pt-1 pb-1 ui selection dropdown search w-full'}),
            'origin': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'destination': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'reference_number': forms.TextInput(attrs={'autocomplete': 'new-password', 'class': 'text-sm pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'shipment_value': forms.NumberInput(attrs={'autocomplete': 'new-password', 'class': 'text-sm pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'currency': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'reason_for_export': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'incoterms': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'shipment_terms': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown pt-1 pb-1 ui selection dropdown search w-full'}),
            'content': forms.Textarea(attrs={'autocomplete': 'new-password', 'class': 'text-sm pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'rows': 1}),
            'forwarding_number': forms.Textarea(attrs={'autocomplete': 'new-password', 'class': 'text-sm pt-1 pb-1 peer block w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['vendor'].user = self.user
        self.fields['agency'].queryset = Agency.objects.filter(
            is_blocked=False)

        prefix = "awb_"
        for name, field in self.fields.items():
            field.widget.attrs['id'] = prefix + name
            field.widget.attrs['name'] = prefix + name

        # Set initial currency to USD if not set
        if not self.initial.get('currency') and not (self.data and self.data.get('awb_currency')):
            try:
                usd_currency = Currency.objects.get(name="USD")
                self.fields['currency'].initial = usd_currency.pk
            except Exception as e:
                pass

        # Set initial origin to Nepal if not set
        if not self.initial.get('origin') and not (self.data and self.data.get('origin')):
            try:
                nepal = Country.objects.get(name="NEPAL")
                self.fields['origin'].initial = nepal.pk
            except Exception as e:
                pass

        # Update vendor queryset based on selected hub
        if 'awb-hub' in self.data:
            try:
                hub_id = int(self.data.get('awb-hub'))
                print("Hub id: ", hub_id)
                self.fields['vendor'].queryset = Vendor.objects.filter(
                    hub_vendor__id=hub_id)
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.hub:
            self.fields['vendor'].queryset = Vendor.objects.filter(
                hub_vendor=self.instance.hub)

        # Update product_type and service querysets based on selected vendor
        if 'awb-vendor' in self.data:
            try:
                vendor_id = int(self.data.get('awb-vendor'))
                print("Vendor id: ", vendor_id)
                self.fields['product_type'].queryset = ProductType.objects.filter(
                    vendor__id=vendor_id)
                self.fields['service'].queryset = Service.objects.filter(
                    vendor__id=vendor_id)
            except (ValueError, TypeError):
                pass

            print("Self vendor: ", self.fields['vendor'].queryset)
        elif self.instance and self.instance.vendor:
            self.fields['product_type'].queryset = ProductType.objects.filter(
                vendor=self.instance.vendor)
            self.fields['service'].queryset = Service.objects.filter(
                vendor=self.instance.vendor)
            print("got here: ", self.fields['vendor'].queryset,
                  self.fields['product_type'].queryset, self.fields['service'].queryset)

    def clean(self):
        cleaned_data = super().clean()
        print("Cleaned data: ", self.data)
        is_cash_user = cleaned_data.get('is_cash_user', False)
        agency = cleaned_data.get('agency')
        hub = cleaned_data.get('hub')
        vendor = cleaned_data.get('vendor')

        if not is_cash_user and not agency:
            self.add_error('agency', 'Agency is required if not cash user.')

        if is_cash_user and agency:
            self.add_error('agency', 'Agency is not allowed if cash user.')

        if hub and vendor and not vendor.hub_vendor.filter(id=hub.id).exists():
            self.add_error(
                'vendor', 'Selected vendor is not associated with the chosen hub.')

        if self.user.role == 'agencyuser' and is_cash_user:
            self.add_error(
                'agency', "Cash user is not allowed for agency."
            )

        return cleaned_data


class AWBUpdateForm(forms.ModelForm):
    is_custom = forms.BooleanField(
        label="Custom AWB Number",
        required=False,
        disabled=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'text-sm form-checkbox pt-1 pb-1 h-5 w-5 bg-gray-300 text-gray-600 rounded border-gray-300 focus:ring-gray-500',
            }
        )
    )

    awbno = forms.CharField(
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full pt-1 pb-1 text-sm appearance-none border border-gray-300 bg-gray-300 px-3 pt-1 pb-1 text-gray-800 rounded-md',
            'autocomplete': 'off'
        })
    )
    dividing_factor = CustomModelChoiceField(
        queryset=DividingFactor.objects.all(),
        widget=forms.Select(attrs={
            "id": "box_total_dividing_factor",
            "class": "peer block pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 rounded-md",
            "required": True
        }),
        required=True,
        initial=DividingFactor.objects.first()
    )
    is_cash_user = forms.BooleanField(
        initial=False,
        required=False,
        disabled=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'text-sm form-checkbox pt-1 pb-1 h-5 w-5 text-gray-600 rounded border-gray-300 focus:ring-gray-500',
        })
    )
    hub = forms.ModelChoiceField(
        queryset=Hub.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'autocomplete': 'new-password',
            'class': 'text-sm small-dropdown ui selection dropdown search w-full'
        })
    )
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.filter(is_blocked=False),
        required=False,
        disabled=True,
        widget=forms.Select(attrs={
            'class': 'text-sm small-dropdown ui selection dropdown search w-full py-0',
            'autocomplete': 'none'
        })
    )
    company = forms.ModelChoiceField(
        label="C O M P A N Y",
        queryset=Company.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'autocomplete': 'none',
            'class': 'text-sm small-dropdown ui selection dropdown search w-full',
        })
    )

    vendor = VendorModelChoiceField(
        queryset=Vendor.objects.none(),
        required=False,
        user=None,
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
    )

    product_type = forms.ModelChoiceField(
        required=False,
        queryset=ProductType.objects.none(),
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
    )
    service = forms.ModelChoiceField(
        required=False,
        queryset=Service.objects.none(),
        widget=forms.Select(
            attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
    )

    class Meta:
        model = AWBDetail
        fields = ['is_cash_user', 'is_custom', 'awbno', 'reference_number', 'agency', 'company', 'hub', 'vendor', 'origin', 'destination', 'product_type', 'service', 'shipment_value', 'currency', 'content',
                  'forwarding_number',   'dividing_factor', 'reason_for_export', 'incoterms', 'shipment_terms']
        widgets = {
            'company': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'vendor': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'origin': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'destination': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'product_type': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'service': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'reference_number': forms.TextInput(attrs={'autocomplete': 'new-password', 'class': 'text-sm peer block pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'shipment_value': forms.NumberInput(attrs={'autocomplete': 'new-password', 'class': 'text-sm peer block  pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'currency': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'content': forms.Textarea(attrs={'autocomplete': 'new-password', 'class': 'text-sm peer block pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'rows': 1}),
            'forwarding_number': forms.Textarea(attrs={'autocomplete': 'new-password', 'class': 'text-sm peer block pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white py-3 px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent', 'rows': 1}),
            'reason_for_export': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'incoterms': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'shipment_terms': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['vendor'].user = user
        prefix = "awb_"
        for name, field in self.fields.items():
            field.widget.attrs['id'] = prefix + name
            field.widget.attrs['name'] = prefix + name

        # Set initial currency to USD if not set
        if not self.initial.get('currency') and not (self.data and self.data.get('awb_currency')):
            try:
                usd_currency = Currency.objects.get(name="USD")
                self.fields['currency'].initial = usd_currency.pk
            except Exception as e:
                pass

        # Set initial origin to Nepal if not set
        if not self.initial.get('origin') and not (self.data and self.data.get('origin')):
            try:
                nepal = Country.objects.get(name="NEPAL")
                self.fields['origin'].initial = nepal.pk
            except Exception as e:
                pass

        # Update vendor queryset based on selected hub
        if 'awb-hub' in self.data:
            try:
                hub_id = int(self.data.get('awb-hub'))
                print("Hub id: ", hub_id)
                self.fields['vendor'].queryset = Vendor.objects.filter(
                    hub_vendor__id=hub_id)
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.hub:
            self.fields['vendor'].queryset = Vendor.objects.filter(
                hub_vendor=self.instance.hub)

        # Update product_type and service querysets based on selected vendor
        if 'awb-vendor' in self.data:
            try:
                vendor_id = int(self.data.get('awb-vendor'))
                print("Vendor id: ", vendor_id)
                self.fields['product_type'].queryset = ProductType.objects.filter(
                    vendor__id=vendor_id)
                self.fields['service'].queryset = Service.objects.filter(
                    vendor__id=vendor_id)
            except (ValueError, TypeError):
                pass

            print("Self vendor: ", self.fields['vendor'].queryset)
        elif self.instance and self.instance.vendor:
            self.fields['product_type'].queryset = ProductType.objects.filter(
                vendor=self.instance.vendor)
            self.fields['service'].queryset = Service.objects.filter(
                vendor=self.instance.vendor)
            print("got here: ", self.fields['vendor'].queryset,
                  self.fields['product_type'].queryset, self.fields['service'].queryset)

    def clean(self):
        cleaned_data = super().clean()
        is_cash_user = cleaned_data.get('is_cash_user', False)
        agency = cleaned_data.get('agency', None)
        hub = cleaned_data.get('hub')
        vendor = cleaned_data.get('vendor')

        if not is_cash_user and not agency:
            self.add_error('agency', 'Agency is required if not cash user.')

        if is_cash_user and agency:
            self.add_error('agency', 'Agency is not allowed if cash user.')

        if hub and vendor and not vendor.hub_vendor.filter(id=hub.id).exists():
            self.add_error(
                'vendor', 'Selected vendor is not associated with the chosen hub.')

        return cleaned_data


class ConsigneeForm(forms.ModelForm):
    post_zip_code = forms.CharField(
        label="P O S T A L   C O D E",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'autocomplete': 'none'
        })
    )

    class Meta:
        model = Consignee
        fields = ['person_name', 'company',  'address1', 'address2',    'post_zip_code', 'city', 'state_county', 'state_abbreviation', 'email_address', 'phone_number', 'phone_number_2',
                  'document_type', 'document_number']
        widgets = {
            'document_type': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'document_front': forms.FileInput(attrs={'autocomplete': 'none', 'class': 'text-sm pt-1 pb-1 ui file input'}),
            'document_back': forms.FileInput(attrs={'autocomplete': 'none', 'class': 'text-sm pt-1 pb-1 ui file input'}),
            'company': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'person_name': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'phone_number': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'phone_number_2': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'email_address': forms.EmailInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'post_zip_code': forms.TextInput(attrs={'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'city': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'state_abbreviation': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'state_county': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'address1': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'address2': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full pt-1 pb-1 appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'document_number': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block pt-1 pb-1 w-full appearance-none border border-gray-300 bg-white px-3 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prefix = "consignee_"
        for name, field in self.fields.items():
            field.widget.attrs['id'] = prefix + name
            field.widget.attrs['name'] = prefix + name


class ConsignorForm(forms.ModelForm):
    post_zip_code = forms.CharField(
        label="P O S T A L   C O D E",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'autocomplete': 'none'
        })
    )

    class Meta:
        model = Consignor
        fields = ['person_name', 'company',  'address1', 'address2',  'post_zip_code', 'city', 'state_county', 'phone_number',  'email_address',
                  'document_type', 'document_number', 'document_front', 'document_back']
        widgets = {
            'document_type': forms.Select(attrs={'autocomplete': 'none', 'class': 'text-sm small-dropdown ui selection dropdown search w-full'}),
            'document_front': forms.FileInput(attrs={'autocomplete': 'none', 'class': 'text-sm ui file input'}),
            'document_back': forms.FileInput(attrs={'autocomplete': 'none', 'class': 'text-sm ui file input'}),
            'company': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'person_name': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'phone_number': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'email_address': forms.EmailInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),

            'post_zip_code': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'state_abbreviation': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'city': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'state_county': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'address1': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'address2': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
            'document_number': forms.TextInput(attrs={'autocomplete': 'none', 'class': 'text-sm peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prefix = "consignor_"
        for name, field in self.fields.items():
            field.widget.attrs['id'] = prefix + name
            field.widget.attrs['name'] = prefix + name


class BoxDetailsForm(forms.ModelForm):
    box_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    volumetric_weight = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    charged_weight = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )

    class Meta:
        model = BoxDetails
        fields = ['box_number', 'length', 'breadth', 'height',
                  'actual_weight', 'volumetric_weight', 'charged_weight']
        widgets = {
            'length': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md', 'required': True}),
            'breadth': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md', 'required': True}),
            'height': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md', 'required': True}),
            'actual_weight': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # For existing instances, set the id as the primary key and use the computed box number.
            self.initial['id'] = self.instance.pk
            self.initial['box_number'] = f"Box-{self.instance.get_box_number()}"
        else:
            try:
                box_num = int(self.prefix.split('-')[-1]) + 1
                self.initial['box_number'] = f"Box-{box_num}"
            except Exception:
                self.initial['box_number'] = "Box-?"


class BoxItemForm(forms.ModelForm):
    # Use a Select widget for box_number; its choices will be updated dynamically in the view.
    box_number = forms.CharField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'text-sm  w-full peer block border border-gray-300 bg-white text-sm rounded-md'
        })
    )
    amount = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    unit_weight = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
        })
    )

    class Meta:
        model = BoxItem
        fields = ['description', 'hs_code', 'quantity',
                  'unit_type', 'unit_weight', 'unit_rate']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
            }),
            'hs_code': forms.TextInput(attrs={
                'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md',
            }),
            'unit_rate': forms.NumberInput(attrs={
                'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
            }),
            'unit_type': forms.Select(attrs={
                'class': 'text-sm  w-full peer block border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_type'].empty_label = None
        # Do not hardcode choices here—the view will update


class BoxUpdateForm(forms.ModelForm):
    id = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    box_number = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    volumetric_weight = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    charged_weight = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )
    bag_no = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = BoxDetails
        fields = ['id', 'box_awb_no', 'box_number',  'length', 'breadth', 'height',
                  'actual_weight', 'volumetric_weight', 'charged_weight', 'bag_no']
        widgets = {
            'box_awb_no': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'}),
            'length': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'}),
            'breadth': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'}),
            'height': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'}),
            'actual_weight': forms.TextInput(attrs={'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'}),
        }


class BoxItemUpdateForm(forms.ModelForm):
    id = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True
        })
    )
    box_number = forms.CharField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'text-sm w-full peer block border border-gray-300 bg-white text-sm rounded-md'
        })
    )
    amount = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-sm peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-gray-300 rounded-md',
            'readonly': True,
            'tabindex': '-1'
        })
    )

    class Meta:
        model = BoxItem
        fields = ['id', 'description', 'hs_code', 'quantity',
                  'unit_type', 'unit_weight', 'unit_rate']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
            'hs_code': forms.TextInput(attrs={'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
            'unit_weight': forms.NumberInput(attrs={'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
            'unit_rate': forms.NumberInput(attrs={'class': 'text-sm peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
            'unit_type': forms.Select(attrs={'class': 'text-sm w-full peer block border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_type'].empty_label = None
        # Compute amount dynamically
        try:
            quantity = float(self.data.get(
                f'{self.prefix}-quantity') or self.initial.get('quantity', 0))
            rate = float(self.data.get(
                f'{self.prefix}-unit_rate') or self.initial.get('unit_rate', 0))
            self.fields['amount'].initial = quantity * rate
        except Exception:
            self.fields['amount'].initial = None


class ForwardinNumberUploadForm(forms.Form):
    via = forms.ChoiceField(
        choices=[('SHIPMENT', 'SHIPMENT')],
        widget=forms.Select(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 rounded-md',
            'required': True
        })
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 rounded-md',
            'required': True
        })
    )


class AWBStatusForm(forms.ModelForm):
    class Meta:
        model = AWBStatus
        fields = ['status', 'location', 'created_at']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'
            }),
            'created_at': forms.DateTimeInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md',
                'type': 'datetime-local'
            })
        }

    def __init__(self, *args, **kwargs):
        self.awb = kwargs.pop('awb', None)  # ✅ Must pop before super()
        super().__init__(*args, **kwargs)

        # Set initial value for created_at to current time if not provided
        if not self.instance.pk and not self.data.get('created_at'):
            from django.utils import timezone
            self.fields['created_at'].initial = timezone.now()

        if self.awb:
            existing_statuses = AWBStatus.objects.filter(
                awb=self.awb).values_list('status', flat=True)

            # Normalize the existing statuses to prevent mismatch
            existing_statuses = [status.strip().upper()
                                 for status in existing_statuses]

            self.fields['status'].choices = [
                (value, label) for value, label in self.fields['status'].choices
                if value.strip().upper() not in existing_statuses
            ]

            # Get the latest status if it exists
            latest_status = AWBStatus.objects.filter(
                awb=self.awb).order_by('-created_at').first()
            if latest_status and latest_status.status.strip().upper() not in existing_statuses:
                self.fields['status'].initial = latest_status.status

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.awb:
            instance.awb = self.awb
        if commit:
            instance.save()
        return instance


class UpdateForwardingNumberForm(forms.Form):
    awbno = forms.CharField(widget=forms.HiddenInput())
    forwarding_number = forms.CharField(widget=forms.HiddenInput())


class UpdateBoxAWBNumberForm(forms.Form):
    box_awb_no = forms.CharField(widget=forms.HiddenInput())
    box_id = forms.IntegerField(widget=forms.HiddenInput())
