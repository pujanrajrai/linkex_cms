from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import re
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.http import QueryDict
import json
import pandas as pd
import json
import re
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from accounts.models.agency import AgencyRequest

from accounts.models import Agency, Module, AgencyAccess, User, DividingFactor
from accounts.pages.users.forms import UserForm, UserUpdateForm
from .forms import AgencyAccessFormSet, AgencyForm, AgencyRequestForm     # RateFormSet
from django.http import JsonResponse, QueryDict, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.db.models import Q
from hub.pages.hub.forms import UploadHubRateForm
from .forms import AgencyForm, AgencyHubForm
from django.http import JsonResponse
from django.http import HttpResponse
from io import BytesIO
from decorators import has_roles
from django.contrib.auth.decorators import login_required




@login_required
@has_roles(['admin'])
def agency_list(request):
    """List all Agencies."""
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        post_dict = QueryDict(request.POST.urlencode(), mutable=True)
        params_search = post_dict.get('columns')
        params_search_value = post_dict.get('search')
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)

        object_list = Agency.objects.all()

        count = object_list.count()
        column_map = {
            1: 'company_name',
            2: 'owner_name'
        }
        
        search_value = request.POST.get('search[value]', '')
        if search_value:
            object_list = object_list.filter(
                Q(company_name__icontains=search_value) |
                Q(owner_name__icontains=search_value)
            )
        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'desc')
        order_field = column_map.get(order_column_index, 'created_at')
        if order_dir == "asc":
            order_field = '-' + order_field

        # for index, field in column_map.items():
        #     column_search_value = request.POST.get(f'columns[{index}][search][value]', '').strip()
        #     if column_search_value:
        #         kwargs = {f"{field}__icontains": column_search_value}
        #         object_list = object_list.filter(**kwargs)

        filtered_total = object_list.count()
        # Always add created_at as secondary ordering for consistency
        object_list = object_list.order_by(
            order_field, '-created_at')[param_start:param_start + param_limit]

        # object_list = object_list[param_start:param_limit + param_start]

        row = list(object_list.values())

        context = {
            'draw': post_dict.get('draw'),
            'recordsTotal': count,
            'recordsFiltered': filtered_total,
            'data': row,

            "current": "agency",
            
        }

        data = mark_safe(json.dumps(context, indent=4,
                         sort_keys=True, default=str))
        return HttpResponse(data, content_type='application/json')

    return render(request, "accounts/agency/list.html" , {"title": "Agency"})


@login_required
@has_roles(['admin'])
def agency_request_list(request):
    """List all Agencies request."""
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))

    if not requested_html:
        post_dict = QueryDict(request.POST.urlencode(), mutable=True)
        params_search = post_dict.get('columns')
        params_search_value = post_dict.get('search')
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)

        object_list = AgencyRequest.everything.all()

        count = object_list.count()

        search_value = request.POST.get('search[value]', '')
        if search_value:
            object_list = object_list.filter(
                Q(company_name__icontains=search_value) |
                Q(owner_name__icontains=search_value)
            )

        filtered_total = object_list.count()
        object_list = object_list[param_start:param_limit + param_start]

        row = list(object_list.values())

        context = {
            'draw': post_dict.get('draw'),
            'recordsTotal': count,
            'recordsFiltered': filtered_total,
            'data': row,

            "current": "agency",
        }

        data = mark_safe(json.dumps(context, indent=4,
                         sort_keys=True, default=str))
        return HttpResponse(data, content_type='application/json')
    return render(request, "accounts/agency/request_list.html", {"title": "Agency Request"})


@login_required
@has_roles(['admin'])
def agency_create(request):
    """Create a new Agency."""
    initial_agency = {}
    initial_user = {}
    agency_req = None
    from_request_id = request.GET.get("from_request")

    if from_request_id:
        try:
            agency_req = AgencyRequest.objects.get(id=from_request_id)

            initial_agency = {
                'company_name': agency_req.company_name,
                'owner_name': agency_req.owner_name,
                'email': agency_req.email,
                'country': agency_req.country,
                'zip_code': agency_req.zip_code,
                'state': agency_req.state,
                'city': agency_req.city,
                'address1': agency_req.address1,
                'address2': agency_req.address2,
                'contact_no_1': agency_req.contact_no_1,
                'contact_no_2': agency_req.contact_no_2,
                'company_pan_vat': agency_req.company_pan_vat,
                'citizenship_front': agency_req.citizenship_front,
                'citizenship_back': agency_req.citizenship_back,
                'passport': agency_req.passport,


            }

            initial_user = {
                'full_name': agency_req.owner_name,
                'email': agency_req.email,
                'contact_no': agency_req.contact_no_1
            }
            if agency_req.contact_no_2 and agency_req.contact_no_2.isdigit():
                initial_user['contact_no'] = int(
                    agency_req.contact_no_2)

        except AgencyRequest.DoesNotExist:
            messages.warning(request, "Agency Request not found.")
            return redirect("accounts:pages:agency:request_list")

    # Forms handling
    if request.method == "POST":
        form = AgencyForm(request.POST, request.FILES)
        user_form = UserForm(request.POST)

        if form.is_valid() and user_form.is_valid():
            try:
                with transaction.atomic():
                    agency = form.save(commit=False)

                    if agency_req:
                        if not agency.logo and agency_req.logo:
                            agency.logo = agency_req.logo
                        if not agency.company_pan_vat and agency_req.company_pan_vat:
                            agency.company_pan_vat = agency_req.company_pan_vat
                        if not agency.citizenship_front and agency_req.citizenship_front:
                            agency.citizenship_front = agency_req.citizenship_front
                        if not agency.citizenship_back and agency_req.citizenship_back:
                            agency.citizenship_back = agency_req.citizenship_back
                        if not agency.passport and agency_req.passport:
                            agency.passport = agency_req.passport

                    # Save the agency with files
                    agency.save()

                    # Now create default agency user
                    user = user_form.save(commit=False)
                    user.agency = agency
                    user.role = 'agencyuser'
                    user.is_default_user = True
                    user.username = user.email
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()
                    if from_request_id:
                        if AgencyRequest.objects.get(id=from_request_id):
                            AgencyRequest.objects.get(
                                id=from_request_id).delete()
                messages.success(
                    request, "Agency created successfully !")
                return redirect("accounts:pages:agency:detail", pk=agency.pk)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        # GET request - initialize forms
        form = AgencyForm(initial=initial_agency)
        user_form = UserForm(initial=initial_user)

        # If we have a agency_req with files, manually set the file fields
        if agency_req:
            # This is just for display in the form
            form.fields['logo'].initial = agency_req.logo
            form.fields['company_pan_vat'].initial = agency_req.company_pan_vat
            form.fields['citizenship_front'].initial = agency_req.citizenship_front
            form.fields['citizenship_back'].initial = agency_req.citizenship_back
            form.fields['passport'].initial = agency_req.passport

    return render(request, "accounts/agency/create.html", {
        "form": form,
        "user_form": user_form,
        "title": "Agency",
        "agency_req": agency_req  # Pass this to the template to access file fields
    })


@login_required
@has_roles(['admin'])
def agency_update(request, pk):
    """Update an existing Agency."""
    agency = get_object_or_404(Agency, pk=pk)

    if request.method == "POST":
        form = AgencyForm(request.POST, request.FILES, instance=agency)

        if form.is_valid():
            try:
                with transaction.atomic():
                    agency = form.save()

                messages.success(request, "Agency updated successfully!")
                return redirect("accounts:pages:agency:detail", pk=agency.pk)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

    form = AgencyForm(instance=agency)

    context = {
        "form": form,
        "title": "Agency"
    }

    return render(request, "accounts/agency/update.html", context)


@login_required
@has_roles(['admin'])
def add_agency_hub_rate(request, pk):
    """Add a new Hub Rate for an Agency."""
    agency = get_object_or_404(Agency, pk=pk)

    AgencyHubRateFormSet = forms.formset_factory(
        form=HubRateUpdateForm,
        extra=0
    )

    if request.method == "POST":
        hub_form = BillingZoneServiceForm(request.POST)
        formset = AgencyHubRateFormSet(request.POST)

        if hub_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                billing_zone_service = hub_form.save()
                for form in formset:
                    weight_range = form.cleaned_data.get('weight_range')
                    rate = form.cleaned_data.get('rate')
                    AgencyHubRate.objects.update_or_create(
                        agency=agency,
                        billing_zone_service=billing_zone_service,
                        weight_range=weight_range,
                        defaults={'rate': rate}
                    )
            messages.success(request, "Hub rates updated successfully!")
            return redirect("accounts:pages:agency:detail", pk=agency.pk)
    else:
        initial_data = []
        for weight_range in WeightRange.objects.all().order_by('starting'):
            initial_data.append({
                'weight_range': weight_range,
                'ending': weight_range.ending if weight_range.ending else None
            })

        formset = AgencyHubRateFormSet(initial=initial_data)
        hub_form = BillingZoneServiceForm()
    context = {
        "formset": formset,
        "hub_form": hub_form,
        "agency": agency,
        "is_adding": True,
        "title": "Agency"
    }
    return render(request, "accounts/agency/add_agency_hub_rate.html", context)


# @login_required
# @has_roles(['admin'])
# def upload_agency_hub_rate(request, pk):
#     agency = get_object_or_404(Agency, pk=pk)
#     if request.method != "POST":
#         messages.error(request, "Invalid request method")
#         return redirect(request.META.get('HTTP_REFERER', '/'))

#     hubs = Hub.objects.all()
#     form = UploadHubRateForm(request.POST, request.FILES)

#     if form.is_valid():
#         file = form.cleaned_data.get('file')
#         try:
#             if file.name.endswith('.csv'):
#                 df = pd.read_csv(file)
#             elif file.name.endswith(('.xlsx', '.xls')):
#                 df = pd.read_excel(file)
#             else:
#                 messages.error(
#                     request, "Invalid file format. Please upload CSV or Excel file.")
#                 return redirect(request.META.get('HTTP_REFERER', '/'))
#         except Exception as e:
#             messages.error(request, f"Error reading file: {str(e)}")
#             return redirect(request.META.get('HTTP_REFERER', '/'))

#         df.fillna('', inplace=True)

#         # Preload WeightRanges
#         weight_range_map = {}
#         for wr in WeightRange.objects.all():
#             weight_range_map[(wr.starting, wr.ending)] = wr

#         # Preload existing AgencyHubRates
#         existing_rates = AgencyHubRate.objects.filter(agency=agency)
#         rate_map = {(r.hub_id, r.weight_range_id): r for r in existing_rates}

#         new_weight_ranges = []
#         new_rates = []
#         updates = []

#         hub_name_to_id = {hub.name: hub.id for hub in hubs}

#         has_errors = False

#         for index, row in df.iterrows():
#             weight_str = str(row.get('WEIGHT')).strip()

#             if not weight_str:
#                 df.at[index, 'WEIGHT_ERROR'] = 'Missing weight'
#                 has_errors = True
#                 continue

#             try:
#                 if '-' in weight_str:
#                     starting, ending = map(float, weight_str.split('-'))
#                 elif weight_str.endswith('Plus'):
#                     starting = float(weight_str[:-4])
#                     ending = 10000000
#                 else:
#                     starting = float(weight_str)
#                     ending = None
#             except ValueError:
#                 df.at[index, 'WEIGHT_ERROR'] = 'Invalid weight format'
#                 has_errors = True
#                 continue

#             # Find or prepare WeightRange
#             range_obj = weight_range_map.get((starting, ending))
#             if not range_obj:
#                 range_obj = WeightRange(starting=starting, ending=ending)
#                 new_weight_ranges.append(range_obj)
#                 weight_range_map[(starting, ending)] = range_obj

#             for hub_name, hub_id in hub_name_to_id.items():
#                 if hub_name in df.columns:
#                     rate_value = row.get(hub_name)
#                     if rate_value:
#                         try:
#                             rate_value = float(rate_value)
#                             if rate_value < 0:
#                                 df.at[index,
#                                       f'{hub_name}_ERROR'] = 'Negative rate not allowed'
#                                 has_errors = True
#                                 continue
#                         except ValueError:
#                             df.at[index, f'{hub_name}_ERROR'] = 'Invalid rate'
#                             has_errors = True
#                             continue

#                         # Check if exists already
#                         key = (hub_id, range_obj.id)
#                         existing = rate_map.get(key)

#                         if existing:
#                             if existing.rate != rate_value:
#                                 existing.rate = rate_value
#                                 updates.append(existing)
#                         else:
#                             new_rates.append(AgencyHubRate(
#                                 agency=agency,
#                                 hub_id=hub_id,
#                                 weight_range=range_obj,
#                                 rate=rate_value
#                             ))

#         # Save all new WeightRanges
#         if new_weight_ranges:
#             WeightRange.objects.bulk_create(new_weight_ranges)
#             for wr in new_weight_ranges:
#                 weight_range_map[(wr.starting, wr.ending)] = wr

#         # Save all new AgencyHubRates
#         if new_rates:
#             AgencyHubRate.objects.bulk_create(new_rates, batch_size=500)

#         # Save all updated AgencyHubRates
#         if updates:
#             AgencyHubRate.objects.bulk_update(
#                 updates, ['rate'], batch_size=500)

#         if has_errors:
#             output = BytesIO()
#             with pd.ExcelWriter(output, engine='openpyxl') as writer:
#                 df.to_excel(writer, index=False, sheet_name='Sheet1')

#             response = HttpResponse(
#                 output.getvalue(),
#                 content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             )
#             response['Content-Disposition'] = 'attachment; filename=agency_hub_rate_errors.xlsx'

#             messages.warning(
#                 request, "Some errors were found. Please check the downloaded file for details.")
#             return response

#         messages.success(request, "Agency hub rates uploaded successfully!")
#         return redirect("accounts:pages:agency:detail", pk=agency.pk)

#     else:
#         messages.error(request, f"Error uploading hub rate: {form.errors}")
#         return redirect(request.META.get('HTTP_REFERER', '/'))




@login_required
@has_roles(['admin'])
def upload_agency_hub_rate(request, pk):
    agency = get_object_or_404(Agency, pk=pk)
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    hubs = Hub.objects.all()
    form = UploadHubRateForm(request.POST, request.FILES)

    if form.is_valid():
        file = form.cleaned_data.get('file')
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                messages.error(
                    request, "Invalid file format. Please upload CSV or Excel file.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            messages.error(request, f"Error reading file: {str(e)}")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        df.fillna('', inplace=True)

        # Preload WeightRanges
        weight_range_map = {}
        for wr in WeightRange.objects.all():
            weight_range_map[(wr.starting, wr.ending)] = wr


        has_errors = False

        for index, row in df.iterrows():
            weight_str = str(row.get('WEIGHT')).strip()

            if not weight_str:
                df.at[index, 'WEIGHT_ERROR'] = 'Missing weight'
                has_errors = True
                continue

            try:
                if '-' in weight_str:
                    starting, ending = map(float, weight_str.split('-'))
                elif weight_str.endswith('Plus'):
                    starting = float(weight_str[:-4])
                    ending = 10000000
                else:
                    starting = float(weight_str)
                    ending = None
            except ValueError:
                df.at[index, 'WEIGHT_ERROR'] = 'Invalid weight format'
                has_errors = True
                continue

            range_obj = weight_range_map.get((starting, ending))
            if not range_obj:
                range_obj = WeightRange(starting=starting, ending=ending)
                weight_range_map[(starting, ending)] = range_obj

            for col in df.columns:
                if col == "WEIGHT" or col.endswith("_ERROR"):
                    continue

                try:
                    hub_name, billing_zone, service = col.split("-")
                    print(f"HUB NAME: {hub_name}, BILLING ZONE: {billing_zone}, SERVICE: {service}")

                except ValueError:
                    has_errors = True
                    df.at[index, f"{col}_ERROR"] = "Invalid format"
                    continue

                try:
                    hub = Hub.objects.get(name=hub_name)
                    hub_bz = HubBillingZone.objects.get(hub=hub, name=billing_zone)
                    bz_service = BillingService.objects.get(name=service)
                    hub_bz_service = HubBillingZoneService.objects.get(
                        hub_billing_zone=hub_bz,
                        billing_service=bz_service
                    )
                except Hub.DoesNotExist:
                    has_errors = True
                    df.at[index, f"{col}_ERROR"] = "Hub not found: {hub_name}"
                    continue

                except HubBillingZone.DoesNotExist:
                    has_errors = True
                    df.at[index, f"{col}_ERROR"] = "Billing zone not found: {billing_zone}"
                    continue

                except HubBillingZoneService.DoesNotExist:
                    has_errors = True
                    df.at[index, f"{col}_ERROR"] = "Billing service not found: {service}"
                    continue

                try:
                    rate = float(row.get(col))
                    if rate < 0:
                        has_errors = True
                        df.at[index, f"{col}_ERROR"] = "Negative rate not allowed"
                        continue
                except ValueError:
                    has_errors = True
                    df.at[index, f"{col}_ERROR"] = "Invalid rate"
                    continue

                AgencyHubRate.objects.update_or_create(
                    agency=agency,
                    weight_range=range_obj,
                    billing_zone_service=hub_bz_service,
                    defaults={'rate': rate}
                )

        if has_errors:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=agency_hub_rate_errors.xlsx'

            messages.warning(
                request, "Some errors were found. Please check the downloaded file for details.")
            return response

        messages.success(request, "Agency hub rates uploaded successfully!")
        return redirect("accounts:pages:agency:detail", pk=agency.pk)

    else:
        messages.error(request, f"Error uploading hub rate: {form.errors}")
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@has_roles(['admin'])
def edit_agency_hub_rate(request, agency_pk, bzs_pk):
    """Edit Agency Hub Rate"""
    agency = get_object_or_404(Agency, pk=agency_pk)
    bzs = get_object_or_404(HubBillingZoneService, pk=bzs_pk)

    # Get all weight ranges and prepare initial data
    initial_data = []
    weight_ranges = WeightRange.objects.all().order_by('starting')

    # For each weight range, get the corresponding rate if it exists
    for weight_range in weight_ranges:
        rate = AgencyHubRate.objects.filter(
            agency=agency,
            billing_zone_service=bzs,
            weight_range=weight_range
        ).values_list('rate', flat=True).first()

        initial_data.append({
            'weight_range': weight_range,
            'rate': rate if rate else 0,
            'ending': weight_range.ending if weight_range.ending else None
        })

    AgencyHubRateFormSet = forms.formset_factory(
        form=HubRateUpdateForm,
        extra=0
    )

    if request.method == "POST":
        formset = AgencyHubRateFormSet(request.POST)
        if formset.is_valid():
            try:
                for form, weight_range in zip(formset, weight_ranges):
                    rate = form.cleaned_data.get('rate')
                    AgencyHubRate.objects.update_or_create(
                        agency=agency,
                        billing_zone_service=bzs,
                        weight_range=weight_range,
                        defaults={'rate': rate}
                    )
                messages.success(
                    request, "Agency hub rates updated successfully!")
                return redirect("accounts:pages:agency:detail", pk=agency_pk)
            except Exception as e:
                messages.error(request, f"Error updating rates: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        formset = AgencyHubRateFormSet(initial=initial_data)

    composite = (
        f"{bzs.hub_billing_zone.hub.name} – "
        f"{bzs.hub_billing_zone.name} – "
        f"{bzs.billing_service.name}"
    )
    context = {
        "formset": formset,
        "agency": agency,
        "title": "Agency",
        "composite": composite
    }
    return render(request, "accounts/agency/add_agency_hub_rate.html", context)


@login_required
def agency_detail(request, pk):
    agency = get_object_or_404(Agency, pk=pk)
    if not (request.user.role == 'admin' or (request.user.agency and request.user.agency.pk == agency.pk)):
        messages.error(request, "You don't have permission to view this agency.")
        return redirect("accounts:pages:agency:detail", pk=request.user.agency.pk)


    upload_form = UploadHubRateForm()
    context = {
        "agency": agency,
        "users": User.objects.filter(agency=agency),
        "upload_form": upload_form,
        "title": "Agency"
    }
    return render(request, "accounts/agency/detail.html", context)


@login_required
@has_roles(['admin'])
def agency_block(request, pk):
    """Block an Agency."""
    agency = get_object_or_404(Agency, pk=pk)
    agency.is_blocked = True
    agency.save()
    messages.success(request, f"Agency {agency.company_name} blocked successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def agency_unblock(request, pk):
    """Unblock an Agency."""
    agency = get_object_or_404(Agency, pk=pk)
    agency.is_blocked = False
    agency.save()
    messages.success(request, f"Agency {agency.company_name} unblocked successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin', 'agencyuser'])
def add_user_in_agency(request, pk):
    user = request.user
    agency = get_object_or_404(Agency, pk=pk)
    can_add_user = False
    if agency.users.count() >= agency.max_user:
        messages.error(request, "Agency has reached its maximum user limit.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if agency.is_blocked:
        messages.error(
            request, "Agency is blocked. Unblock the agency to add user.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.user.role == 'admin':
        can_add_user = True
    if request.user.role == 'agencyuser' and request.user.is_default_user:
        if user.agency == agency:
            can_add_user = True

    if not can_add_user:
        messages.error(
            request, "You don't have permission to add user to this agency.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.pop('password')
            user = User.objects.create(
                **form.cleaned_data,
                username=form.cleaned_data.get('username'),
                agency=agency,
                role='agencyuser'
            )
            user.set_password(password)
            user.save()
            return redirect("accounts:pages:agency:detail", pk=agency.pk)
    context = {
        "form": form,
        "title": "Agency"
    }
    return render(request, "accounts/user/create.html", context)


@csrf_exempt
def user_history_by_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    if request.method == 'POST':
        param_start = int(request.POST.get('start', 0))
        param_limit = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')

        users = User.objects.filter(agency__id=agency_id)
        if search_value:
            users = users.filter(
                Q(full_name__icontains=search_value)  # Search by full_name
            )
        history_data = []
        for user in users:
            history_entries = user.history.all().order_by(
                '-history_date')[param_start:param_limit + param_start]
            if search_value:
                history_entries = history_entries.filter(
                    Q(history_user__full_name__icontains=search_value)
                )
            history_entries = history_entries[param_start:param_limit + param_start]

            for entry in history_entries:
                changes = []
                ignored_fields = ["id", "updated_at", "history_id", "history_date",
                                  "history_type", "history_change_reason", "history_user"]

                if entry.history_type == "+":
                    creator = entry.history_user.full_name if entry.history_user else "System"

                if entry.prev_record:
                    for field in entry.prev_record._meta.fields:
                        if field.name in ignored_fields:
                            continue
                        old_value = getattr(
                            entry.prev_record, field.name, None)
                        new_value = getattr(entry, field.name, None)

                        if old_value != new_value:
                            changes.append(
                                f"{field.verbose_name}: {old_value} → {new_value}")
                else:
                    changes.append("Created")
                    creator = entry.history_user.full_name if entry.history_user else "System"

                changed_by = entry.history_user.full_name if entry.history_user else creator if creator else "System"

                history_data.append({
                    "user": user.full_name,
                    "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "changed_by": changed_by,
                    "changes": changes,
                })

        # Return a JSON response for DataTable
        context = {
            'draw': int(request.POST.get('draw', 1)),
            'recordsTotal': len(users),
            'recordsFiltered': len(history_data),
            'data': history_data
        }
        return JsonResponse(context)

    else:
        return render(request, 'accounts/agency/user_history_by_agency.html', {'agency': agency})


@login_required
@has_roles(['admin'])
def agency_hub_rate_history(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    # Check if this is a DataTables AJAX request
    if request.method == 'POST':
        agency_hub_rates = AgencyHubRate.objects.filter(
            agency=agency)

        history_data = []
        seen_entries = set()
        for rate in agency_hub_rates:
            history_entries = rate.history.all().order_by('-history_date')

            for entry in history_entries:
                changes = []
                ignored_fields = ["id", "updated_at", "history_id", "history_date",
                                  "history_type", "history_change_reason", "history_user"]

                if entry.history_type == "+":
                    creator = entry.history_user.full_name if entry.history_user else "System"
                    changes.append("Created")
                elif entry.history_type == "~":
                    for field in entry.prev_record._meta.fields:
                        if field.name in ignored_fields:
                            continue

                        old_value = getattr(
                            entry.prev_record, field.name, None)
                        new_value = getattr(entry, field.name, None)

                        if old_value != new_value:
                            changes.append(
                                f"{field.verbose_name}: {old_value} → {new_value}")

                    if changes:
                        creator = entry.history_user.full_name if entry.history_user else "System"

                if not changes:
                    continue

                changed_by = entry.history_user.full_name if entry.history_user else creator if creator else "System"

                entry_identifier = (
                    rate.hub.id, rate.weight_range.id, entry.history_date)

                if entry_identifier not in seen_entries:
                    seen_entries.add(entry_identifier)

                    history_data.append({
                        "hub": rate.hub.name,
                        "weight_range": str(rate.weight_range),
                        "rate": str(rate.rate),
                        "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "changed_by": changed_by,
                        "changes": changes,
                    })

        # Return JSON response for DataTables
        return JsonResponse({
            'draw': int(request.POST.get('draw', 1)),
            'recordsTotal': len(history_data),
            'recordsFiltered': len(history_data),
            'data': history_data
        })

    # For initial page load, just render the template
    return render(request, 'accounts/agency/agency_hub_rate_history.html', {"agency": agency})


# @login_required
# def get_agency_dividing_factor(request, agency_pk=None):
#     print(request.GET.get('is_updating'))
#     is_updating = request.GET.get('is_updating') == 'true'
#     if is_updating and request.user.role == 'admin':
#         queryset = DividingFactor.objects.values_list('id', 'name', 'factor')
#         dividing_factors = list(queryset.values('id', 'name', 'factor'))
#         return JsonResponse(dividing_factors, safe=False)
#     if agency_pk and agency_pk != 0:
#         agency = Agency.objects.get(pk=agency_pk)
#         queryset = agency.dividing_factor.values_list('id', 'name', 'factor')
#     else:
#         queryset = DividingFactor.objects.values_list('id', 'name', 'factor')

#     dividing_factors = list(queryset.values('id', 'name', 'factor'))
#     return JsonResponse(dividing_factors, safe=False)


@csrf_exempt
def submit_agency_request(request):
    if request.method == 'POST':
        request_form = AgencyRequestForm(request.POST, request.FILES)
        if request_form.is_valid():
            request_form.save()
            return JsonResponse({'message': 'Request submitted successfully!'})
        else:
            return JsonResponse({'errors': request_form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
