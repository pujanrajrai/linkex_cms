from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Currency
from .forms import CurrencyForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def currency_list(request):
    currencies = Currency.everything.all()
    context = {"currencies": currencies, "current": "shipment_master", "title": "Currency",}
    return render(request, 'awb/master/currency/list.html', context)


@login_required
@has_roles(['admin'])
def currency_create(request):
    form = CurrencyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Currency created successfully!")
            return redirect('awb:pages:master:currency:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Currency",}
    return render(request, 'awb/master/currency/create.html', context)


@login_required
@has_roles(['admin'])
def currency_update(request, pk):
    currency = get_object_or_404(Currency, pk=pk)
    form = CurrencyForm(request.POST or None, instance=currency)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Currency updated successfully!")
            return redirect('awb:pages:master:currency:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Currency",}
    return render(request, 'awb/master/currency/update.html', context)


@login_required
@has_roles(['admin'])
def currency_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        currency = get_object_or_404(Currency, pk=pk)
        try:
            currency.delete()
            messages.success(request, "Currency deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:currency:list"))
