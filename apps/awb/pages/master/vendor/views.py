# unit_type/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hub.models import Vendor
from .forms import VendorForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def vendor_list(request):
    vendors = Vendor.everything.all().prefetch_related('manifest_format')
    context = {"vendors": vendors,
               "current": "vendor_master", "title": "Vendor"}
    return render(request, 'awb/master/vendor/list.html', context)


@login_required
@has_roles(['admin'])
def vendor_create(request):
    form = VendorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Vendor created successfully!")
            return redirect('awb:pages:master:vendor:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "vendor_master", "title": "Vendor"}
    return render(request, 'awb/master/vendor/create.html', context)


@login_required
@has_roles(['admin'])
def vendor_update(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    form = VendorForm(request.POST or None, instance=vendor)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Vendor updated successfully!")
            return redirect('awb:pages:master:vendor:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "vendor_master", "title": "Vendor"}
    return render(request, 'awb/master/vendor/update.html', context)


@login_required
@has_roles(['admin'])
def vendor_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            vendor = get_object_or_404(Vendor, pk=pk)
            vendor.delete()
            messages.success(request, "Vendor deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:vendor:list"))
