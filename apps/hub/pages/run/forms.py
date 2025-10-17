from django.utils import timezone
from django.utils.timezone import now
from accounts.models import Company
from django import forms
from django.forms import inlineformset_factory
from hub.models import Run, RunAWB, RunStatus, Hub
from awb.models import AWBDetail, BoxDetails
from hub.utils import AWBValidator
from django.core.exceptions import ValidationError
from awb.models.awb import status_choices
from hub.models import Vendor


class BoxDetailsForm(forms.ModelForm):
    actual_weight = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full border border-gray-300 bg-gray-100 px-3 py-1 text-sm rounded-md text-left',
            'tabindex': "-1",
            'readonly': True
        })
    )
    volumetric_weight = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full border border-gray-300 bg-gray-100 px-3 py-1 text-sm rounded-md text-left',
            'tabindex': "-1",
            'readonly': True
        })
    )
    charged_weight = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full border border-gray-300 bg-gray-100 px-3 py-1 text-sm rounded-md text-left',
            'tabindex': "-1",
            'readonly': True
        })
    )
    awb_no = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full border border-gray-300 bg-gray-100 px-3 py-1 text-sm rounded-md text-left',
            'tabindex': "-1",
            'readonly': True
        })
    )

    class Meta:
        model = BoxDetails
        fields = ['bag_no']
        widgets = {
            'bag_no': forms.NumberInput(attrs={
                'class': 'peer block w-full border border-gray-300 bg-white px-3 py-1 text-sm rounded-md'
            }),
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)

        # Make bag_no required
        self.fields['bag_no'].required = True

        # If an instance with a valid AWB exists, use its data and add autofocus
        if self.instance and getattr(self.instance, 'awb', None):
            self.fields['awb_no'].initial = self.instance.awb.awbno
            self.fields['actual_weight'].initial = self.instance.actual_weight
            self.fields['volumetric_weight'].initial = self.instance.volumetric_weight
            self.fields['charged_weight'].initial = self.instance.charged_weight
            # Add autofocus to bag_no field when AWB exists
            self.fields['bag_no'].widget.attrs['autofocus'] = True
        else:
            # Otherwise, fallback to provided initial data (if any).
            self.fields['awb_no'].initial = initial.get('awb_no', '')
            self.fields['actual_weight'].initial = initial.get(
                'actual_weight', 0)
            self.fields['volumetric_weight'].initial = initial.get(
                'volumetric_weight', 0)
            self.fields['charged_weight'].initial = initial.get(
                'charged_weight', 0)


class RunForm(forms.ModelForm):

    class Meta:
        model = Run
        fields = ['company', 'hub', 'vendor', 'run_no', 'flight_no',
                  'flight_departure_date', 'mawb_no', 'manifest']
        widgets = {
            'company': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'hub': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'vendor': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'run_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'flight_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'flight_departure_date': forms.DateInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
                'type': 'date'
            }),
            'mawb_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'manifest': forms.SelectMultiple(attrs={
                'class': 'ui selection dropdown search multiple w-full',
                'data-placeholder': 'Please filter AWBs first'
            })
        }


class RunUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make company and hub readonly if this is an update
        if self.instance and self.instance.pk:
            self.fields['company'].disabled = True
            self.fields['hub'].disabled = True

    class Meta:
        model = Run
        fields = ['company', 'hub', 'vendor', 'run_no', 'flight_no',
                  'flight_departure_date', 'mawb_no', 'manifest']
        widgets = {
            'company': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'hub': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'vendor': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'run_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'flight_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'flight_departure_date': forms.DateInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
                'type': 'date'
            }),
            'mawb_no': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
            }),
            'manifest': forms.SelectMultiple(attrs={
                'class': 'ui selection dropdown search multiple w-full',
                'data-placeholder': 'Please filter AWBs first'
            })
        }


class AddAWBForm(forms.ModelForm):
    awb = forms.ModelMultipleChoiceField(
        queryset=AWBDetail.objects.filter(is_in_run=False),
        required=False,
        label="AWB",
        widget=forms.SelectMultiple(attrs={
            'class': 'ui selection dropdown search multiple w-full',
            'data-placeholder': 'Please filter AWBs first'
        })
    )


class AddAWBToRunForm(forms.Form):
    awb_number = forms.CharField(
        label='AWB Number',
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white-100 px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )
    bagging_number = forms.CharField(
        label='Bag Details',
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )
    forwarding_number = forms.CharField(
        label='Forwarding Number',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )
    total_boxes = forms.IntegerField(
        label='Total Boxes',
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': True,
            'disabled': True,
            'tabindex': "-1",
            'class': 'peer block w-full appearance-none border border-gray-300 bg-gray-100 px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )
    aw_vw_cw = forms.CharField(
        label='AW-VW-CW',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'disabled': True,
            'tabindex': "-1",
            'class': 'peer block w-full appearance-none border border-gray-300 bg-gray-100 px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )
    consignee_consignor_destination = forms.CharField(
        label='Consignee-Consignor-Destination',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'disabled': True,
            'tabindex': "-1",
            'class': 'peer block w-full appearance-none border border-gray-300 bg-gray-400 px-1 pt-1 pb-1 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
        })
    )

    def __init__(self, *args, run=None, **kwargs):
        self.run = run
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # If all fields are empty, return without validation
        if not any(cleaned_data.values()):
            return cleaned_data

        awb_number = cleaned_data.get('awb_number')
        bagging_numbers = cleaned_data.get('bagging_number', '').split(
            ',') if cleaned_data.get('bagging_number') else []

        if not awb_number:
            return cleaned_data

        try:
            awb = AWBDetail.objects.get(awbno=awb_number)
            boxes = BoxDetails.objects.filter(awb=awb).order_by('created_at')

            # Store AWB and boxes for use in the view
            cleaned_data['awb'] = awb
            cleaned_data['boxes'] = boxes

            # Validate AWB using utility functions
            if self.run:
                try:
                    AWBValidator.validate_awb_verified(awb)
                    AWBValidator.validate_awb_company_and_hub(awb, self.run)
                    AWBValidator.validate_awb_not_in_run(awb, self.run)
                except ValidationError as e:
                    self.add_error('awb_number', str(e))
                    # Keep the entered data in cleaned_data
                    return cleaned_data

            # Validate number of boxes matches number of bag numbers
            if bagging_numbers and boxes:
                if len(bagging_numbers) != boxes.count():
                    self.add_error('bagging_number',
                                   f"Number of bag numbers ({len(bagging_numbers)}) does not match number of boxes ({boxes.count()}) for AWB {awb_number}"
                                   )
                    return cleaned_data

                # Validate bag number format
                for idx, bag_num in enumerate(bagging_numbers):
                    try:
                        int(bag_num.strip())
                    except ValueError:
                        self.add_error('bagging_number',
                                       f"Invalid bag number format at position {idx + 1} for AWB {awb_number}"
                                       )
                        return cleaned_data

            # Set the display fields
            cleaned_data['total_boxes'] = boxes.count()
            cleaned_data['aw_vw_cw'] = f"{awb.total_actual_weight} - {awb.total_volumetric_weight} - {awb.total_charged_weight}"
            cleaned_data['consignee_consignor_destination'] = (
                f"{awb.consignee.person_name if awb.consignee else ''} - "
                f"{awb.consignor.person_name if awb.consignor else ''} - "
                f"{awb.destination.short_name if awb.destination else ''}"
            )

        except AWBDetail.DoesNotExist:
            self.add_error('awb_number', f"AWB {awb_number} not found")
            # Keep the entered data in cleaned_data
            return cleaned_data

        return cleaned_data


class RunStatusForm(forms.ModelForm):
    status = forms.ChoiceField(choices=status_choices)
    created_at = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
            'type': 'datetime-local'
        })
    )

    class Meta:
        model = RunStatus
        fields = ['created_at', 'status', 'location']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'ui selection dropdown search w-full'
            }),
            'created_at': forms.DateInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 bg-white px-3 pt-3 pb-2 text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'peer block w-full appearance-none border border-gray-300 px-3 pt-1 pb-1 text-gray-800 bg-white rounded-md'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.run = kwargs.pop('run', None)
        super().__init__(*args, **kwargs)

        local_now = timezone.localtime(timezone.now())
        self.fields['created_at'].initial = local_now.strftime(
            '%Y-%m-%dT%H:%M')
        self.fields['location'].initial = "Kathmandu"

        if self.run:
            # ✅ use prefetched statuses from the view (no extra queries)
            statuses = list(
                self.run.runstatus_set.all().order_by("-created_at"))

            existing_statuses = [s.status.strip().upper() for s in statuses]

            self.fields['status'].choices = [
                (value, label) for value, label in self.fields['status'].choices
                if value.strip().upper() not in existing_statuses
            ]

            if statuses:
                self.fields['status'].initial = statuses[0].status
