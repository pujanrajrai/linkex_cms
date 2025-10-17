# unit_type/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hub.models.hub import Vendor
from awb.models import UnitType
from .forms import UnitTypeForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def unit_type_list(request):
    unit_types = UnitType.everything.all()
    context = {"unit_types": unit_types, "current": "unit_type_master", "title": "UnitType"}
    return render(request, 'awb/master/unit_type/list.html', context)


@login_required
@has_roles(['admin'])
def unit_type_create(request):
    form = UnitTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Unit Type created successfully!")
            return redirect('awb:pages:master:unit_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "unit_type_master", "title": "UnitType"}
    return render(request, 'awb/master/unit_type/create.html', context)


@login_required
@has_roles(['admin'])
def unit_type_update(request, pk):
    unit_type = get_object_or_404(UnitType, pk=pk)
    form = UnitTypeForm(request.POST or None, instance=unit_type)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Unit Type updated successfully!")
            return redirect('awb:pages:master:unit_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "unit_type_master", "title": "UnitType"}
    return render(request, 'awb/master/unit_type/update.html', context)


@login_required
@has_roles(['admin'])
def unit_type_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            unit_type = get_object_or_404(UnitType, pk=pk)
            unit_type.delete()
            messages.success(request, "Unit Type deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:unit_type:list"))



@login_required
@has_roles(['admin', 'agencyuser'])
def get_vendor_unit_type(request, vendor_pk):
    vendor = get_object_or_404(Vendor, pk=vendor_pk)
    unit_types = UnitType.everything.filter(vendor=vendor)
    return JsonResponse(list(unit_types.values('id', 'name')), safe=False)
