# service/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from awb.models import Service
from .forms import ServiceForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def service_list(request):
    services = Service.everything.all()
    context = {"services": services, "current": "service_master",  "title": "Service"}
    return render(request, 'awb/master/service/list.html', context)


@login_required
@has_roles(['admin'])
def service_create(request):
    form = ServiceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Service created successfully!")
            return redirect('awb:pages:master:service:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "service_master",  "title": "Service"}
    return render(request, 'awb/master/service/create.html', context)


@login_required
@has_roles(['admin'])
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Service updated successfully!")
            return redirect('awb:pages:master:service:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "service_master",  "title": "Service"}
    return render(request, 'awb/master/service/update.html', context)


@login_required
@has_roles(['admin'])
def service_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            service = get_object_or_404(Service, pk=pk)
            service.delete()
            messages.success(request, "Service deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:service:list"))





@login_required
@has_roles(['admin', 'agencyuser'])
def get_services_with_vendor(request, vendor_pk):
    try:
        services = Service.objects.filter(vendor__pk=vendor_pk)
        data = [
            {
                'id': service.id,
                'name': service.name
            }
            for service in services
            for vendor in service.vendor.filter(pk=vendor_pk)
        ]
        return JsonResponse(data, safe=False)
    except:
        return JsonResponse([], safe=False)
