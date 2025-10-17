from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hub.models import ManifestFormat
from .forms import ManifestForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def manifest_list(request):
    manifests = ManifestFormat.everything.all()
    context = {
        "manifests": manifests,
        "current": "shipment_master", "title": "ManifestFormat",
    }
    return render(request, 'awb/master/manifest/list.html', context)


@login_required
@has_roles(['admin'])
def manifest_create(request):
    form = ManifestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Manifest created successfully!")
            return redirect('awb:pages:master:manifest:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "ManifestFormat",}
    return render(request, 'awb/master/manifest/create.html', context)


@login_required
@has_roles(['admin'])
def manifest_update(request, pk):
    manifest = get_object_or_404(ManifestFormat, pk=pk)
    form = ManifestForm(request.POST or None, instance=manifest)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Manifest updated successfully!")
            return redirect('awb:pages:master:manifest:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "ManifestFormat",}
    return render(request, 'awb/master/manifest/update.html', context)


@login_required
@has_roles(['admin'])
def manifest_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            manifest = ManifestFormat.everything.filter(pk=pk).first()
            if manifest:
                manifest.delete()
                messages.success(request, "Manifest deleted successfully!")
            else:
                messages.error(
                    request, "Manifest not found. It might have been deleted already.")
        except IntegrityError:
            messages.error(
                request, "Cannot delete manifest as it is linked to other records. Contact Admin!")
        except Exception:
            messages.error(
                request, "An unexpected error occurred. Please contact the administrator if the issue persists.")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:manifest:list"))
