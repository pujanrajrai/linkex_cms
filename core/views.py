from awb.apis.utils import track_awb
from awb.models import AWBDetail, AWBStatus
from accounts.pages.agency.forms import AgencyRequestForm
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import HttpResponse, JsonResponse
import re
import json
from django.apps import apps
from django.shortcuts import redirect
from django.shortcuts import render
from decorators import has_roles
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from home.models import Service, FAQ, MyCompany, ProhibitedItems
User = get_user_model()


def agency_request(request):
    if request.method == "POST":
        form = AgencyRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your request has been submitted successfully. We will get back to you soon.")
            return redirect("agency_request")
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = AgencyRequestForm()

    context = {
        "request_form": form,  # Pass the form instance, not the class
    }
    return render(request, "agency_request.html", context)


def tracking(request):
    context = {
        "request_form": AgencyRequestForm,
        "tracking_no":  request.GET.get("tracking_no", "").strip(),
    }

    if not context["tracking_no"]:
        return render(request, "tracking.html", context)

    result = track_awb(context["tracking_no"])
    if "error" in result:
        context["error"] = result["error"]
    else:
        context["timeline"] = result.get("timeline", [])
        context["awb"] = result.get("awb")

        # Check if forwarding number is assigned for additional info display
        if context["awb"] and context["awb"].get("forwarding_number"):
            context["has_forwarding_number"] = True

        # Check for hold status in timeline
        context["is_on_hold"] = False
        context["hold_location"] = ""
        if context["timeline"]:
            for item in context["timeline"]:
                if "ON HOLD" in item.get("status", "").upper() or "HOLD" in item.get("status", "").upper():
                    context["is_on_hold"] = True
                    context["hold_location"] = item.get("location", "")
                    break

    return render(request, "tracking.html", context)


@login_required
@has_roles(['admin'])
def history_list(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        object_id = request.POST.get('object_id')

    else:
        model_name = request.GET.get('model_name')
        object_id = request.GET.get('object_id')

    print("model_name", model_name)
    print("object_id", object_id)

    # Find the actual model class
    model = None
    if model_name == 'User':
        model_class = User
    else:
        # Loop through all installed apps to find the correct model
        for app_config in apps.get_app_configs():
            try:
                model_class = app_config.get_model(model_name)
                break  # Stop searching once the model is found
            except LookupError:
                continue  # Keep searching in other apps

    if model_class is None:
        messages.error(request, "Model not found")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    requested_html = re.search(
        r'^text/html', request.META.get('HTTP_ACCEPT', ''))

    if not requested_html:
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)
        search_value = request.POST.get('search[value]', '')

        try:
            obj = model_class.objects.get(id=object_id)
            history_entries = model_class.history.filter(
                id=object_id).order_by('-history_date')

            if search_value:
                history_entries = history_entries.filter(
                    Q(changes__icontains=search_value) |
                    Q(changed_by__icontains=search_value)
                )

            count = history_entries.count()
            filtered_total = history_entries.count()

            history_entries = history_entries[param_start:param_limit + param_start]

            history_data = []
            for entry in history_entries:
                changes = []
                ignored_fields = ["id", "updated_at", "history_id", "history_date",
                                  "history_type", "history_change_reason", "history_user"]
                creator = "System"  # Default creator

                if entry.history_type == "+":
                    creator = entry.history_user.full_name if entry.history_user else "System"

                if entry.prev_record:
                    for field in entry.prev_record._meta.fields:
                        if field.name in ignored_fields:
                            continue  # Skip ignored fields

                        old_value = getattr(
                            entry.prev_record, field.name, None)
                        new_value = getattr(entry, field.name, None)

                        if old_value != new_value:  # Only store changed fields
                            changes.append(
                                f"{field.verbose_name}: {old_value} → {new_value}")
                else:
                    changes.append("Created")

                changed_by = entry.history_user.full_name if entry.history_user else creator

                history_data.append({
                    "date": entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "changed_by": changed_by,
                    "changes": changes,
                })

            context = {
                'draw': int(request.POST.get('draw', 1)),
                'recordsTotal': count,
                'recordsFiltered': filtered_total,
                'data': history_data,
            }

            return JsonResponse(context)

        except model_class.DoesNotExist:
            return JsonResponse({
                'draw': int(request.POST.get('draw', 1)),
                'recordsTotal': 0,
                'recordsFiltered': 0,
                'data': [],
                'error': f"Object with ID {object_id} not found"
            })

    # For regular HTML requests
    context = {
        "model_name": model_name,
        "obj": model_class.objects.get(id=object_id) if object_id else None
    }
    return render(request, 'history_list.html', context)


def get_deleted_models(request):
    # For regular HTML request, just render the template
    if request.method == 'GET':
        return render(request, 'deleted_models_history.html')

    # For DataTables AJAX request
    if request.method == 'POST':
        # Pagination parameters
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        draw = int(request.POST.get('draw', 1))
        search_value = request.POST.get('search[value]', '')

        deleted_data = []
        column_map = {
            1: 'model_name',
            2: 'instance_id',
            3: 'deleted_at',
            4: 'deleted_by',
            5: 'change_reason',
            6: 'deletion_type',
        }

        order_column_index = int(request.POST.get(
            'order[0][column]', 3))  # Default to deleted_at
        order_dir = request.POST.get('order[0][dir]', 'desc')
        order_key = column_map.get(order_column_index, 'deleted_at')

        for model in apps.get_models():
            # Skip User model
            if model.__name__ == 'User':
                continue

            if hasattr(model, 'history'):
                # Hard deleted entries (from history)
                try:
                    history_qs = model.history.filter(
                        history_type='-').select_related('history_user')
                    if search_value:
                        history_qs = history_qs.filter(
                            Q(history_change_reason__icontains=search_value) |
                            Q(id__icontains=search_value) |
                            Q(history_user__username__icontains=search_value)
                        )

                    deleted_data.extend([{
                        'model_name': model.__name__,
                        'instance_id': entry.id,
                        'deleted_at': entry.history_date,
                        'deleted_at_formatted': entry.history_date.strftime("%Y-%m-%d %H:%M:%S"),
                        'deleted_by': getattr(entry.history_user, 'full_name', 'System') if entry.history_user else 'System',
                        'change_reason': entry.history_change_reason or 'Not specified',
                        'deletion_type': 'Hard Delete'
                    } for entry in history_qs])
                except Exception as e:
                    print(f"[History Error] {model.__name__}: {e}")

            # Check for soft deleted entries if the model has that capability
            if hasattr(model, 'everything') and hasattr(model, 'is_deleted'):
                try:
                    soft_deleted_entries = model.everything.filter(
                        is_deleted=True)

                    # Apply search if provided
                    if search_value:
                        soft_deleted_entries = soft_deleted_entries.filter(
                            Q(id__icontains=search_value)
                        )

                    for soft_entry in soft_deleted_entries:
                        deleted_data.append({
                            'model_name': model.__name__,
                            'instance_id': soft_entry.id,
                            'deleted_at': soft_entry.updated_at,  # Keep as datetime for sorting
                            'deleted_at_formatted': soft_entry.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                            'deleted_by': 'System',  # Modify if you track who soft deleted
                            'change_reason': 'Soft deleted',
                            'deletion_type': 'Soft Delete',
                            # 'restore_url': reverse('restore_soft_deleted', kwargs={'model_name': model.__name__, 'record_id': soft_entry.id})
                        })
                except Exception as e:
                    # Handle any errors in soft delete retrieval
                    print(
                        f"Error fetching soft deleted entries for {model.__name__}: {e}")

        deleted_data.sort(key=lambda x: x.get(order_key, ''),
                          reverse=(order_dir == 'desc'))

        total_records = len(deleted_data)

        paginated_data = deleted_data[start:start + length]

        data = [{
            'sn': i,
            'model_name': entry['model_name'],
            'instance_id': entry['instance_id'],
            'deleted_at': entry['deleted_at_formatted'],
            'deleted_by': entry['deleted_by'],
            'change_reason': entry['change_reason'],
            'deletion_type': entry['deletion_type'],
        } for i, entry in enumerate(paginated_data, start=start+1)]

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })

    return render(request, 'deleted_models_history.html')


def home(request):
    context = {}
    tracking_no = request.GET.get('tracking_no')
    if tracking_no:
        try:
            awb = AWBDetail.objects.get(awbno=tracking_no)

            # Define status order
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
                default=Value(len(status_choices_order)),
                output_field=IntegerField(),
            )

            awbstatus = AWBStatus.objects.filter(
                awb=awb).order_by(status_order)
            context["awbstatus"] = awbstatus
            context["awb"] = awb

        except AWBDetail.DoesNotExist:
            context["error"] = "AWB not found"

        except Exception as e:
            context["error"] = str(e)

        context["tracking_no"] = tracking_no
    context['request_form'] = AgencyRequestForm
    context['services'] = Service.objects.all()
    context['faqs'] = FAQ.objects.all()
    context['company'] = MyCompany.objects.first()
    context['prohibited_items'] = ProhibitedItems.objects.all()

    return render(request, 'home.html', context)

