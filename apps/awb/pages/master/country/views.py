from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Country
from .forms import CountryForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def country_list(request):
    countries = Country.everything.all().order_by('-priority')
    context = {
        "countries": countries,
        "current": "shipment_master",
        "title": "Country",
    }
    return render(request, 'awb/master/country/list.html', context)


@login_required
@has_roles(['admin'])
def country_create(request):
    form = CountryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Country created successfully!")
            return redirect('awb:pages:master:country:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Country", }
    return render(request, 'awb/master/country/create.html', context)


@login_required
@has_roles(['admin'])
def country_update(request, pk):
    country = get_object_or_404(Country, pk=pk)
    form = CountryForm(request.POST or None, instance=country)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Country updated successfully!")
            return redirect('awb:pages:master:country:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Country", }
    return render(request, 'awb/master/country/update.html', context)


@login_required
@has_roles(['admin'])
def country_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            country = Country.everything.filter(pk=pk).first()
            if country:
                country.delete()
                messages.success(request, "Country deleted successfully!")
            else:
                messages.error(
                    request, "Country not found. It might have been deleted already.")
        except IntegrityError:
            messages.error(
                request, "Cannot delete country as it is linked to other records. Contact Admin!")
        except Exception:
            messages.error(
                request, "An unexpected error occurred. Please contact the administrator if the issue persists.")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:country:list"))
