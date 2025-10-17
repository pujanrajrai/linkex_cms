from django.views.decorators.http import require_GET
import re
from openpyxl.worksheet.page import PageMargins

import json
from django.http import HttpResponse, JsonResponse, QueryDict
from django.db.models import Q
from django.utils.safestring import mark_safe
from hub.models import ManifestFormat
from itertools import chain
from .export_utils import RunAWBExporter
import datetime
from django.template.loader import render_to_string
from .utils import RunAWBDetailsFetcher
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from hub.models.run import RunAWB, Run
from .forms import RunForm, AddAWBForm, BoxDetailsForm, RunUpdateForm, AddAWBToRunForm, RunStatusForm
from awb.models import AWBDetail, BoxDetails
from django.db import transaction
from django.contrib import messages
from django.forms import formset_factory
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Count, Case, When, Value, IntegerField
import openpyxl
from openpyxl.utils import get_column_letter
from hub.utils import AWBValidator
from decorators import has_roles
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from hub.models import ManifestFormat, Vendor, Hub
from hub.models import RunStatus


@login_required
@has_roles(['admin'])
def get_vendor_default_manifest(request):
    vendor_id = request.GET.get('vendor_id')
    vendor = get_object_or_404(Vendor, id=vendor_id)
    manifests = vendor.manifest_format.all()
    manifest_list = []
    for manifest in manifests:
        manifest_list.append({
            'id': manifest.id,
            'name': manifest.name,
            'display_name': manifest.display_name
        })
    return JsonResponse(manifest_list, safe=False)


@login_required
@has_roles(['admin'])
def create_run(request):
    form = RunForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                run = form.save(commit=False)
                run.save()  # Save the run first to get an ID
                form.save_m2m()  # Save the many-to-many relationships
                messages.success(request, "Run created successfully!")
                return redirect('hub:pages:run:add_awb', run_id=run.id)
        except Exception as e:
            print(e)
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "run",
               "title": "Run"
               }
    return render(request, 'hub/run/create.html', context)


@login_required
@has_roles(['admin'])
def update_run(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    if run.is_locked:
        messages.error(request, "Run is locked and cannot be updated.")
        return redirect(request.META['HTTP_REFERER'])
    form = RunUpdateForm(request.POST or None, instance=run)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Run updated successfully!")
        if request.GET.get('from_modal') == 'true':
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return redirect('hub:pages:run:add_awb', run_id=run.id)

    context = {"form": form, "run": run, "current": "run",
               "title": "Run", "from_modal": request.GET.get('from_modal')
               }

    if request.headers.get('X-Requested-with') == 'XMLHttpRequest':
        return render(request, 'hub/run/update_run_form.html', context)
    return render(request, 'hub/run/update.html', context)


@login_required
@has_roles(['admin'])
def get_all_awb_from_company_and_hub(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    if run.is_locked:
        messages.error(request, "Run is locked and cannot be updated.")
        return redirect(request.META['HTTP_REFERER'])
    company = run.company
    hub = run.hub
    awbs = AWBDetail.objects.filter(company=company, hub=hub, is_in_run=False)

    try:
        with transaction.atomic():
            for awb in awbs:
                # Create RunAWB entry for each AWB with empty bag_no
                RunAWB.objects.create(
                    run=run,
                    awb=awb,
                )

                # Mark AWB as being in a run
                awb.is_in_run = True
                awb.save()

            messages.success(
                request, f"Successfully added {len(awbs)} AWBs to the run.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('hub:pages:run:add_awb', run_id=run_id)


@login_required
@has_roles(['admin'])
def add_new_awb_to_run(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    if run.is_locked:
        messages.error(request, "Run is locked and cannot be updated.")
        return redirect(request.META['HTTP_REFERER'])
    if request.method == "POST":
        form = AddAWBForm(request.POST)
        if form.is_valid():
            selected_awbs = form.cleaned_data.get('awb')
            if not selected_awbs:
                messages.warning(request, "No AWBs were selected to add.")
                return redirect(request.META['HTTP_REFERER'])

            try:
                with transaction.atomic():
                    count = 0
                    for awb in selected_awbs:
                        RunAWB.objects.create(run=run, awb=awb)
                        awb.is_in_run = True
                        awb.save()
                        count += 1
                    messages.success(
                        request, f"Successfully added {count} AWBs to the run.")
            except Exception as e:
                messages.error(
                    request, f"An error occurred while adding AWBs: {str(e)}")

    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def remove_awb_from_run(request, run_id, awb_no):
    run = get_object_or_404(Run, id=run_id)
    awb = get_object_or_404(AWBDetail, awbno=awb_no)
    run_awb = get_object_or_404(RunAWB.everything, run=run, awb=awb)
    run_awb.delete()
    messages.success(request, "AWB removed from run successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def add_awb_to_run(request, run_id):
    run = get_object_or_404(Run, id=run_id)

    run_awbs = RunAWB.everything.filter(run=run)
    context = {
        "run": run,
        "run_awbs": run_awbs,
        "current": "run",
        "title": "Run"
    }

    # Check for AWB number either via GET or POST
    awb_no = request.GET.get('awb_no') or request.POST.get('awb_no')
    if not awb_no:
        return render(request, 'hub/run/add_awb.html', context)

    try:
        with transaction.atomic():
            awb = get_object_or_404(AWBDetail, awbno=awb_no)
            context.update({'awb': awb, 'awb_no': awb_no})

            # Create formset configuration once
            BoxDetailsFormSet = inlineformset_factory(
                AWBDetail,
                BoxDetails,
                form=BoxDetailsForm,
                fields=('bag_no',),
                extra=0
            )

            # Check existing run AWB and validate in one query
            existing_run_awb = RunAWB.everything.select_related(
                'run').filter(awb=awb).first()

            if existing_run_awb:
                if existing_run_awb.run != run:
                    url = reverse('hub:pages:run:add_awb', kwargs={
                                  'run_id': existing_run_awb.run.id})
                    messages.error(
                        request,
                        f"AWB {awb_no} is already in <a href='{url}' class='underline text-white-600 hover:text-white-800' target='_blank'> #Run {existing_run_awb.run.run_no}</a>"
                    )
                    return redirect(request.path)
            else:
                # Only validate if not already in this run
                try:
                    AWBValidator.validate_awb_verified(awb)
                    AWBValidator.validate_awb_company_and_hub(awb, run)
                    AWBValidator.validate_awb_not_in_run(awb, run)
                except Exception as e:
                    url = reverse('awb:pages:awb:detail',
                                  kwargs={'awb_no': awb_no})
                    messages.error(
                        request,
                        f"{str(e)} <a href='{url}' target='_blank' class='underline text-white-600 hover:text-white-800'>#{awb_no}</a>"
                    )
                    return redirect(request.path)

            if request.method == "POST":
                if run.is_locked:
                    messages.error(
                        request, "Run is locked and cannot be updated.")
                    return redirect(request.META['HTTP_REFERER'])
                formset = BoxDetailsFormSet(request.POST, instance=awb)
                if formset.is_valid():
                    formset.save()
                    if not existing_run_awb:
                        RunAWB.objects.create(run=run, awb=awb)
                    messages.success(
                        request, "AWB details updated successfully")
                    return redirect(request.path)
                messages.error(
                    request, "Invalid form data. Please check and try again.")
            else:
                formset = BoxDetailsFormSet(instance=awb)

            context['formset'] = formset
            return render(request, 'hub/run/add_awb.html', context)

    except Exception as e:
        url = reverse('awb:pages:awb:detail', kwargs={'awb_no': awb_no})
        message = getattr(e, 'message', str(e))
        messages.error(
            request,
            f"An error occurred: {message} <a href='{url}' target='_blank' class='underline text-white-600 hover:text-white-800'>#{awb_no}</a>"
        )
        return redirect(request.path)


@login_required
@has_roles(['admin'])
def list_run(request):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))

    if not requested_html:
        from django.db.models import Count, Sum, Max, Exists, OuterRef
        from awb.models import BoxDetails

        post_dict = QueryDict(request.POST.urlencode(), mutable=True)
        params_search = post_dict.get('columns')
        params_search_value = post_dict.get('search')
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)
        column_map = {
            0: None,
            1: 'run_no',
            2: 'company',
            3: 'hub__hub_code',
            4: 'flight_no',
            5: 'flight_departure_date',
            6: 'mawb_no',
            7: None,
            8: 'annotated_unique_bag_count',
            9: 'annotated_total_charged_weight',
            10: 'annotated_total_boxes',
            11: 'annotated_total_shipment',
            12: 'shipments',
            13: 'annotated_unique_bag_count',
            14: 'annotated_total_actual_weight',
            15: 'annotated_total_volumetric_weight',
            16: 'annotated_total_charged_weight'
        }

        # Optimize queryset with select_related, prefetch_related, and annotations

        object_list = Run.objects.select_related(
            'company', 'hub'
        ).annotate(
            annotated_total_shipment=Count('runawb', distinct=True),

            annotated_total_actual_weight=Sum(
                'runawb__awb__boxdetails__actual_weight'),
            annotated_total_volumetric_weight=Sum(
                'runawb__awb__boxdetails__volumetric_weight'),
            annotated_total_charged_weight=Sum(
                'runawb__awb__boxdetails__charged_weight'),

            annotated_total_boxes=Count(
                'runawb__awb__boxdetails', distinct=True),

            annotated_unique_bag_count=Count(
                'runawb__awb__boxdetails__bag_no', distinct=True),

            annotated_is_departed=Exists(
                RunStatus.objects.filter(
                    run=OuterRef('pk'),
                    status='SHIPMENT DEPARTURED'
                )
            )
        )

        count = Run.objects.count()

        search_value = request.POST.get('search[value]', '')
        if search_value:
            object_list = object_list.filter(
                Q(run_no__icontains=search_value) |
                Q(flight_no__icontains=search_value) |
                Q(hub__name__icontains=search_value) |
                Q(hub__hub_code__icontains=search_value) |
                Q(mawb_no__icontains=search_value)
            )

        filtered_total = object_list.count()
        order_idx = int(request.POST.get('order[0][column]', 1))
        order_dir = request.POST.get('order[0][dir]', 'desc')
        order_field = column_map.get(order_idx)
        if order_field:
            object_list = object_list.order_by(
                order_field if order_dir == 'asc' else f'-{order_field}')
        else:
            object_list = object_list.order_by('-created_at')

        object_list = object_list[param_start:param_limit + param_start]

        # Use annotated values instead of properties
        row = [
            {
                'id': run.id,
                'company_name': f"{run.company.name}",
                'hub_name': f"{run.hub.name}",
                'run_no': run.run_no,
                'flight_no': run.flight_no,
                'flight_departure_date': run.flight_departure_date,
                'mawb_no': run.mawb_no,
                'unique_bag_count': run.annotated_unique_bag_count or 0,
                'total_charged_weight': run.annotated_total_charged_weight or 0,
                'total_boxes': run.annotated_total_boxes or 0,
                'total_shipment': run.annotated_total_shipment or 0,
                'actual_weight': run.annotated_total_actual_weight or 0,
                'volumetric_weight': run.annotated_total_volumetric_weight or 0,
                'is_departed': run.annotated_is_departed,
            }
            for run in object_list
        ]

        context = {
            'draw': post_dict.get('draw'),
            'recordsTotal': count,
            'recordsFiltered': filtered_total,
            'data': row,
            "current": "run"
        }

        data = mark_safe(json.dumps(context, indent=4,
                         sort_keys=True, default=str))
        return HttpResponse(data, content_type='application/json')

    return render(request, 'hub/run/list.html', {"title": "Run"})


@login_required
@has_roles(['admin'])
def export_to_excel(request, run_id):
    run = Run.objects.get(pk=run_id)
    export_type = request.GET.get('type').lower()

    fetcher = RunAWBDetailsFetcher(run_id=run_id)
    details = fetcher.get_details()
    exporter = RunAWBExporter(run, details)

    hub = run.hub.name

    # bag details
    if export_type == "bag_details":
        return exporter.export_bag_details()
    # us bag details
    elif export_type == "us_bag_details":
        return exporter.export_us_bag_details()
    # invoice
    elif export_type == "invoice":
        return exporter.export_invoice()
    # zip
    elif export_type == "invoice_zip":
        return exporter.export_invoice_zip()
    # jkf custom boom
    elif export_type == "export_jfk_bom_custom":
        return exporter.export_jfk_bom_custom()
    # jfk forwarding bom
    elif export_type == "export_jfk_bom_forwarding":
        return exporter.export_jfk_bom_forwarding()
    # jfk manifest
    elif export_type == "export_jfk_manifest":
        return exporter.export_jfk_manifest()
    # uk manifest
    elif export_type == "export_uk_manifest":
        return exporter.export_uk_manifest()
    # aus manifest
    elif export_type == "aus_manifest":
        return exporter.aus_manifest()
    # yyz manifest
    elif export_type == "yyz_manifest":
        return exporter.export_yyz()
    # nepal manifest
    elif export_type == "nepal_manifest":
        return exporter.export_nepal_custom()
    # CDS
    elif export_type == "cds_manifest_ubx_hv":
        fetcher = RunAWBDetailsFetcher(
            run_id=run_id, exclude_country=["CA", "US"])
        details = fetcher.get_details()
        exporter = RunAWBExporter(run, details)
        return exporter.export_cds_manifiest_ubx_us(type="HV")
    elif export_type == "cds_manifest_ubx_ts":
        fetcher = RunAWBDetailsFetcher(
            run_id=run_id, include_country=["CA", "US"])
        details = fetcher.get_details()
        exporter = RunAWBExporter(run, details)
        return exporter.export_cds_manifiest_ubx_us(type="TS")
    # dxb manifest
    elif export_type == "dxb_corierx_manifest":
        return exporter.dxb_corierx_manifest()
    # cfl
    elif export_type == "cfl_excel_unx":
        return exporter.cfl_excel_unx()

    else:
        return HttpResponse("Invalid hub or export type")


@login_required
@has_roles(['admin'])
def run_history(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    run_awbs = RunAWB.objects.filter(run=run)

    if request.method == 'GET':
        return render(request, "hub/run/run_history.html", {
            "run": run,
            "run_awbs": run_awbs,
            "current": "run",
            "title": "Run"
        })

    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')

        run_history = run.history.all()
        run_awb_history = RunAWB.history.filter(run=run)

        box_history = BoxDetails.history.filter(
            awb__in=RunAWB.objects.filter(
                run=run).values_list('awb', flat=True)
        )

        combined_history = sorted(
            chain(run_history, run_awb_history, box_history),
            key=lambda x: x.history_date,
            reverse=True
        )

        history_data = []
        for entry in combined_history:
            changes = {}
            if hasattr(entry, 'prev_record') and entry.prev_record:
                delta = entry.diff_against(entry.prev_record)
                for change in delta.changes:
                    # Handle foreign key changes
                    if change.field.endswith('_id'):
                        related_field = change.field[:-3]
                        try:
                            related_model = getattr(
                                entry.__class__, related_field).field.related_model

                            old_obj = related_model.objects.get(
                                pk=change.old) if change.old is not None else None
                            new_obj = related_model.objects.get(
                                pk=change.new) if change.new is not None else None

                            changes[related_field] = {
                                "old": {field.name: getattr(old_obj, field.name) for field in old_obj._meta.fields} if old_obj else "None",
                                "new": {field.name: getattr(new_obj, field.name) for field in new_obj._meta.fields} if new_obj else "None"
                            }
                        except Exception as e:
                            changes[change.field] = {
                                "old": change.old, "new": change.new}
                    else:
                        changes[change.field] = {
                            "old": change.old, "new": change.new}

            # Determine the model and create history entry
            if isinstance(entry, BoxDetails.history.model):
                history_data.append({
                    "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": "BoxDetails",
                    "changed_by": entry.history_user.full_name if entry.history_user else "System",
                    "history_type": "Created" if entry.history_type == "+" else "Updated" if entry.history_type == "~" else "Deleted",
                    "awb": entry.awb.awbno if entry.awb else "No AWB",
                    "changes": changes,
                })
            elif isinstance(entry, Run.history.model):
                history_data.append({
                    "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": "Run",
                    "changed_by": entry.history_user.full_name if entry.history_user else "System",
                    "history_type": "Created" if entry.history_type == "+" else "Updated" if entry.history_type == "~" else "Deleted",
                    "awb": "N/A",
                    "changes": changes,
                })
            elif isinstance(entry, RunAWB.history.model):
                history_data.append({
                    "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": "RunAWB",
                    "changed_by": entry.history_user.full_name if entry.history_user else "System",
                    "history_type": "Created" if entry.history_type == "+" else "Updated" if entry.history_type == "~" else "Deleted",
                    "awb": entry.awb.awbno if entry.awb else "No AWB",
                    "changes": changes,
                })

        # Apply search filter if provided
        if search_value:
            filtered_data = []
            for entry in history_data:
                if (search_value.lower() in entry['model'].lower() or
                    search_value.lower() in entry['date'].lower() or
                    search_value.lower() in entry['changed_by'].lower() or
                    search_value.lower() in entry['history_type'].lower() or
                    search_value.lower() in entry['awb'].lower() or
                        any(search_value.lower() in str(change).lower() for change in entry['changes'].values())):
                    filtered_data.append(entry)
            history_data = filtered_data

        # Calculate totals
        total_records = len(history_data)
        filtered_total = len(history_data)

        # Apply pagination
        paginated_data = history_data[start:start + length]

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_total,
            'data': paginated_data
        })

    return render(request, "hub/run/run_history.html", {
        "run": run,
        "run_awbs": run_awbs,
        "current": "run",
        "title": "Run"
    })


@login_required
@has_roles(['admin'])
def lock_run(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    run.is_locked = True
    run.save()
    messages.success(request, "Run locked successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def unlock_run(request, run_id):
    run = get_object_or_404(Run, id=run_id)
    run.is_locked = False
    run.save()
    messages.success(request, "Run unlocked successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def new_awb(request, run_id):
    # Optimize run query with select_related
    run = get_object_or_404(Run.objects.select_related(
        'hub', 'company', 'vendor'), id=run_id)
    AWBFormSet = formset_factory(AddAWBToRunForm, extra=1)
    run_status_form = RunStatusForm(request.POST or None, run=run)

    if request.method == "POST":
        formset = AWBFormSet(request.POST, form_kwargs={'run': run})
        if formset.is_valid():
            try:
                with transaction.atomic():
                    valid_forms = [
                        form for form in formset if form.cleaned_data.get('awb_number')]

                    # If all forms are empty, redirect back
                    if not valid_forms:
                        messages.info(
                            request, "No AWBs were added to the run.")
                        return redirect(request.META['HTTP_REFERER'])

                    awb_updates = []
                    box_updates = []
                    awb_instances = []
                    awb_ids = []

                    for form in valid_forms:
                        awb = form.cleaned_data['awb']
                        boxes = form.cleaned_data['boxes']
                        bagging_numbers = form.cleaned_data.get(
                            'bagging_number', '').split(',')
                        forwarding_number = form.cleaned_data.get(
                            'forwarding_number')

                        awb_ids.append(awb.id)

                        # Update AWB forwarding number
                        if forwarding_number:
                            awb.forwarding_number = forwarding_number
                            awb_updates.append(awb)

                        # Update Box bag numbers
                        for idx, box in enumerate(boxes):
                            try:
                                box.bag_no = int(bagging_numbers[idx].strip())
                                box_updates.append(box)
                            except (IndexError, ValueError):
                                continue  # Skip malformed bag numbers

                        awb_instances.append(awb)

                    # Perform bulk updates
                    if awb_updates:
                        AWBDetail.objects.bulk_update(
                            awb_updates, ['forwarding_number'])
                    if box_updates:
                        BoxDetails.objects.bulk_update(box_updates, ['bag_no'])

                    # Avoid duplicate RunAWB entries
                    existing_awb_ids = set(
                        RunAWB.objects.filter(run=run, awb_id__in=awb_ids).values_list(
                            'awb_id', flat=True)
                    )
                    new_run_awbs = [
                        RunAWB(run=run, awb=awb)
                        for awb in awb_instances if awb.id not in existing_awb_ids
                    ]
                    if new_run_awbs:
                        RunAWB.objects.bulk_create(
                            new_run_awbs, ignore_conflicts=True)

                    messages.success(
                        request, "AWBs added to run successfully!")
                    return redirect(request.META['HTTP_REFERER'])

            except Exception as e:
                messages.error(request, str(e))
    else:
        formset = AWBFormSet(form_kwargs={'run': run})

    status_choices_order = [
        'LABEL CREATED',
        'VERIFIED',
        'SHIPMENT HAS BEEN PICKED UP',
        'SHIPMENT PROCESSED',
        'ADDED TO RUN',
        'FORWARDING NO ASSIGNED',
        'SHIPMENT DEPARTURED',
        'SHIPMENT IN TRANSIT',
        'SHIPMENT DELAYED',
        'SHIPMENT ON HOLD',
        'SHIPMENT CUSTOM HELD',
        'SHIPMENT OUT FOR DELIVERY',
        'SHIPMENT DELIVERED',
        'CANCELLED',
    ]

    # Create Case/When expressions for ordering
    status_order = Case(
        *[When(status=status, then=Value(i))
          for i, status in enumerate(status_choices_order)],
        default=Value(99),
        output_field=IntegerField(),
    )

    run_status = RunStatus.objects.filter(run=run).order_by(status_order)

    context = {
        "run": run,
        "formset": formset,
        "current": "run",
        "title": "Run",
        "run_status_form": run_status_form,
        "run_status": run_status,
    }

    return render(request, "hub/run/new_awb.html", context)


def run_awbs_data(request, run_id):
    try:
        run = get_object_or_404(Run, id=run_id)

        run_awbs = RunAWB.objects.filter(run=run).select_related(
            'awb__origin', 'awb__destination', 'awb__consignee', 'awb__consignor',
            'awb__service', 'awb__product_type', 'awb__company', 'awb__hub', 'awb__agency'
        ).prefetch_related('awb__boxdetails')

        data = []
        for awb in run_awbs:
            box_bags = [box.bag_no for box in awb.awb.boxdetails.all()]
            bag_str = ', '.join(str(bag)
                                for bag in box_bags if bag is not None)

            data.append({
                'awb_number': awb.awb.awbno,
                'forwarding_number': awb.awb.forwarding_number,
                'consignee': awb.awb.consignee.person_name,
                'consignor': f"{awb.awb.consignor.company}" if awb.awb.consignor.company else f"{awb.awb.consignor.person_name}",
                'destination': awb.awb.destination.name,
                'actual_weight': awb.awb.total_actual_weight,
                'volumetric_weight': awb.awb.total_volumetric_weight,
                'charged_weight': awb.awb.total_charged_weight,
                'boxes': awb.awb.total_box,
                'bag_numbers': bag_str,
            })

        return JsonResponse({'data': data})

    except Exception as e:
        # Return a useful JSON error to the frontend
        return JsonResponse({'error': str(e)}, status=500)


def manifest_formats_data(request):
    manifest_formats = ManifestFormat.objects.all().values()
    return JsonResponse(list(manifest_formats), safe=False)


@login_required
@has_roles(['admin'])
def update_run_status(request, run_id):
    run = (
        Run.objects
        .prefetch_related("runstatus_set")  # ✅ prevents N+1 queries
        .get(id=run_id)
    )

    run_status_form = RunStatusForm(request.POST or None, run=run)

    if request.method == "POST" and run_status_form.is_valid():
        try:
            with transaction.atomic():
                RunStatus.objects.create(
                    run=run,
                    status=run_status_form.cleaned_data['status'],
                    location=run_status_form.cleaned_data['location'],
                    created_at=run_status_form.cleaned_data['created_at']
                )
                messages.success(request, "Run status updated successfully!")
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e))
    else:
        if request.method == "POST":
            messages.error(
                request, "Invalid form data. Please check and try again.")
            messages.error(request, run_status_form.errors)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def delete_run_status(request, run_status_id):
    run_status = get_object_or_404(RunStatus, id=run_status_id)
    run_status.delete()
    messages.success(request, "Run status deleted successfully!")
    return redirect(request.META['HTTP_REFERER'])


@login_required
@has_roles(['admin'])
def get_awb_details(request):
    awb_no = request.GET.get('awb_no')
    run_id = request.GET.get('run_id')

    if not awb_no:
        return JsonResponse({
            'awb_no': awb_no,
            'error': 'AWB number is required'
        }, status=400)

    try:
        # Optimize run query with select_related
        run = Run.objects.select_related(
            'hub', 'company', 'vendor').get(id=run_id)
    except Run.DoesNotExist:
        return JsonResponse({
            'awb_no': awb_no,
            'error': 'Invalid run ID'
        }, status=400)

    try:
        # Optimize AWB query with comprehensive select_related and prefetch_related
        awb = AWBDetail.objects.select_related(
            'consignee',
            'consignor',
            'agency',
            'destination',
            'origin',
            'company',
            'hub',
            'currency',
            'service',
            'product_type'
        ).prefetch_related('boxdetails').get(awbno=awb_no)

        # Get boxes from prefetched data instead of separate query
        boxes = awb.boxdetails.all()

    except AWBDetail.DoesNotExist:
        return JsonResponse({
            'awb_no': awb_no,
            'error': 'AWB not found'
        }, status=404)

    try:
        # Use AWBValidator to validate all conditions
        AWBValidator.validate_awb_company_and_hub(awb, run)
        AWBValidator.validate_awb_verified(awb)
        AWBValidator.is_run_locked(run)

        # Optimize AWB not in run validation with a single efficient query
        from hub.models.run import RunAWB
        existing_awb_runs = RunAWB.objects.filter(awb=awb).exclude(
            run=run).values_list('run__run_no', flat=True)
        if existing_awb_runs.exists():
            raise ValidationError(
                f"AWB {awb} is already in run(s): {', '.join(existing_awb_runs)}")

    except ValidationError as e:
        return JsonResponse({
            'awb_no': awb_no,
            'error': str(e)
        }, status=400)

    # Get existing bag numbers if any (using prefetched data)
    bag_numbers = [str(box.bag_no) for box in boxes if box.bag_no]
    bagging_details = ','.join(bag_numbers) if bag_numbers else ''

    return JsonResponse({
        "awb_no": awb.awbno,
        "total_boxes": awb.total_box,
        "consignee": awb.consignee.person_name if awb.consignee else '',
        "consignor": awb.consignor.person_name if awb.consignor else '',
        "agency": awb.agency.company_name if awb.agency else '',
        "total_volume": awb.total_volumetric_weight,
        "total_actual_weight": awb.total_actual_weight,
        "total_charged_weight": awb.total_charged_weight,
        "destination": awb.destination.short_name if awb.destination else '',
        "forwarding_number": awb.forwarding_number or '',
        "bagging_details": bagging_details
    })


def get_hub_vendors(request):
    hub_id = request.GET.get('hub_id')
    if not hub_id:
        return JsonResponse({'error': 'hub_id parameter is required'}, status=400)

    hub = get_object_or_404(
        Hub.objects.select_related('currency'),
        pk=hub_id
    )

    vendors = Vendor.objects.filter(hub_vendor__id=hub_id)

    if request.user.role == "admin":
        vendor_list = [
            {
                'id': vendor.id,
                'info': f"{vendor.name} ({vendor.account_number})"
            }
            for vendor in vendors
        ]
    else:
        vendor_list = [
            {
                'id': vendor.id,
                'info': vendor.account_number
            }
            for vendor in vendors
        ]

    return JsonResponse({
        'currency': hub.currency.name,
        'vendors': vendor_list
    })
