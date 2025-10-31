from django import forms
from accounts.models import Agency, AgencyAccess
from accounts.models.masters import DividingFactor, Country
from accounts.models.agency import AgencyRequest
from hub.models import Hub
from .utils import get_modules_count


class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.factor


class AgencyRequestForm(forms.ModelForm):
    class Meta:
        model = AgencyRequest
        fields = [
            'company_name', 'logo', 'owner_name', 'country', 'email', 'zip_code', 'state', 'city',
            'address1', 'address2', 'contact_no_1', 'contact_no_2',  'company_pan_vat', 'citizenship_front', 'citizenship_back', 'passport',

        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'country': forms.Select(attrs={
                'class': 'select2-country w-full px-3 py-2 border border-gray-300 rounded-md focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'state': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'city': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'address1': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'address2': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'contact_no_1': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'contact_no_2': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Nepal as default for country if not already set
        if not self.initial.get('country') and not self.data.get('country'):
            # or the country id if it's a ForeignKey
            try:
                self.initial['country'] = Country.objects.get(name='Nepal')
            except Exception as e:
                pass


class AgencyForm(forms.ModelForm):
    max_user = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        }
        ))
    country = forms.ModelChoiceField(
        label='C O U N T R Y',
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={
            'class': 'ui selection dropdown search w-full p-3',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Agency
        fields = [
            'company_name', 'logo',  'owner_name', 'country', 'email', 'zip_code', 'state', 'city',
            'address1', 'address2', 'contact_no_1', 'contact_no_2', 'credit_limit', 'max_user',
            'custom_per_kg_rate', 'handling_per_box_rate', 'company_pan_vat', 'citizenship_front', 'citizenship_back', 'passport', 'can_verify_awb', 'can_call_api'

        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'state':     forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'city': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'address1': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'address2': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),

            'contact_no_1': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'contact_no_2': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'credit_limit': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'max_user': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'custom_per_kg_rate': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'handling_per_box_rate': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'company_pan_vat': forms.FileInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'citizenship_front': forms.FileInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'citizenship_back': forms.FileInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'passport': forms.FileInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'can_verify_awb': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            }),
            'can_call_api': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            })





        }


class AgencyAccessForm(forms.ModelForm):
    class Meta:
        model = AgencyAccess
        fields = [
            'module',
            'can_create',
            'can_view',
            'can_update',
            'can_delete'
        ]

        widgets = {
            'can_create': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            }),
            'can_view': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            }),
            'can_update': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            }),
            'can_delete': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-primary border-gray-300 rounded-md focus:ring-primary focus:ring-offset-0'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['module'].widget = forms.HiddenInput()


AgencyAccessFormSet = forms.inlineformset_factory(
    Agency,
    AgencyAccess,
    form=AgencyAccessForm,
    extra=get_modules_count(),
    max_num=get_modules_count(),
    can_delete=False
)


class AgencyHubForm(forms.Form):
    hub = forms.ModelChoiceField(
        queryset=Hub.objects.all(),
        widget=forms.Select(attrs={
            'class': 'ui selection dropdown search w-full'
        })
    )
