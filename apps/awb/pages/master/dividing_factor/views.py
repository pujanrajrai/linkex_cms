# dividing_factor/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import DividingFactor
from .forms import DividingFactorForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def dividing_factor_list(request):
    dividing_factors = DividingFactor.everything.all()
    context = {"dividing_factors": dividing_factors,
               "current": "dividing_factor_master", "title": "DividingFactor",}
    return render(request, 'awb/master/dividing_factor/list.html', context)


@login_required
@has_roles(['admin'])
def dividing_factor_create(request):
    form = DividingFactorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Dividing Factor created successfully!")
            return redirect('awb:pages:master:dividing_factor:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "dividing_factor_master", "title": "DividingFactor",}
    return render(request, 'awb/master/dividing_factor/create.html', context)


@login_required
@has_roles(['admin'])
def dividing_factor_update(request, pk):
    dividing_factor = get_object_or_404(DividingFactor, pk=pk)
    form = DividingFactorForm(request.POST or None, instance=dividing_factor)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Dividing Factor updated successfully!")
            return redirect('awb:pages:master:dividing_factor:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "dividing_factor_master", "title": "DividingFactor",}
    return render(request, 'awb/master/dividing_factor/update.html', context)


@login_required
@has_roles(['admin'])
def dividing_factor_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            dividing_factor = get_object_or_404(DividingFactor, pk=pk)
            dividing_factor.delete()
            messages.success(request, "Dividing Factor deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:dividing_factor:list"))
