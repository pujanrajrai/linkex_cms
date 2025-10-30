from django.shortcuts import render
from .models import Company
from django.views.generic import CreateView, UpdateView
from .forms import CompanyForm
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
# Create your views here.
class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "create.html"
    success_url = reverse_lazy('home:company')  
    title = "Create Company"

class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "create.html"
    success_url = reverse_lazy('home:company')
    title = "Update Company"


def get_company(request):
    company = Company.objects.first()
    return render(request, "company.html", {"company_detail": company, "title": "Company"})
