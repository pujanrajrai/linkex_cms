from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Company
from .forms import CompanyForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def company_list(request):
    companies = Company.everything.all().order_by('priority')
    context = {
        "companies": companies,
        "current": "shipment_master", "title": "Company",
    }
    return render(request, 'awb/master/company/list.html', context)


@login_required
@has_roles(['admin'])
def company_create(request):
    form = CompanyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Company created successfully!")
            return redirect('awb:pages:master:company:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Company", }
    return render(request, 'awb/master/company/create.html', context)


@login_required
@has_roles(['admin'])
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Company updated successfully!")
            return redirect('awb:pages:master:company:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "Company", }
    return render(request, 'awb/master/company/update.html', context)


@login_required
@has_roles(['admin'])
def company_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        company = get_object_or_404(Company, pk=pk)
        try:
            company.delete()
            messages.success(request, "Company deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:company:list"))
