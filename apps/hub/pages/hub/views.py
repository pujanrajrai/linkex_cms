from django.db.models import Prefetch
from django.db import models
from itertools import chain
from io import BytesIO
import logging
from django import forms
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
import pandas as pd


from .forms import HubForm, UploadHubRateForm
from hub.models import Hub
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def list_hub(request):
    hubs = Hub.objects.all().select_related(
        'country',
        'currency'
    ).prefetch_related(
        'vendor',
    )

    context = {
        "hubs": hubs,
        "title": "Hub"
    }
    return render(request, 'hub/hub/list.html', context)


@login_required
@has_roles(['admin'])
def hub_detail(request, pk):
    # fetch Hub with its FK relations and M2M vendors in one go
    hub = (
        Hub.objects
        .select_related('country', 'currency')
        .prefetch_related('vendor')
        .get(pk=pk)
    )


    return render(request, 'hub/hub/detail.html', {
        'hub': hub,
        'title': "Hub Details",
        'hub_upload_form': UploadHubRateForm(),
    })


@login_required
@has_roles(['admin'])
def create_hub(request):
    hub_form = HubForm()
    if request.method == "POST":
        hub_form = HubForm(request.POST)
        if hub_form.is_valid():
            hub = hub_form.save()
            return redirect("hub:pages:hub:detail", pk=hub.pk)
    context = {
        "hub_form": hub_form,
        "title": "Hub"
    }
    return render(request, 'hub/hub/create.html', context)


@login_required
@has_roles(['admin'])
def delete_hub(request, pk):
    try:
        hub = get_object_or_404(Hub, pk=pk)
        hub.delete()
        messages.success(request, 'Hub deleted successfully.')
        return redirect("hub:pages:hub:list")
    except Exception as e:
        messages.error(request, f'Error deleting hub: {e}')
        return redirect("hub:pages:hub:list")


@login_required
@has_roles(['admin'])
def update_hub(request, pk):
    hub = get_object_or_404(Hub, pk=pk)
    if request.method == "POST":
        hub_form = HubForm(request.POST, instance=hub)
        # formset = HubRateFormSet(request.POST)

        if hub_form.is_valid():
            with transaction.atomic():
                hub = hub_form.save()

                messages.success(request, "Hub rate updated successfully!")
                return redirect("hub:pages:hub:detail", pk=hub.pk)

    else:
        hub_form = HubForm(instance=hub)

    return render(request, 'hub/hub/update.html', {
        'hub_form': hub_form,
        "title": "Hub"
    })

