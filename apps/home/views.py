from django.shortcuts import render
from .models import MyCompany, Service, FAQ
from django.views.generic import CreateView, UpdateView
from .forms import MyCompanyForm, ServiceForm, FaqForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
class MyCompanyCreateView(LoginRequiredMixin, CreateView):
    model = MyCompany
    form_class = MyCompanyForm
    template_name = "create.html"
    success_url = reverse_lazy('home:company')  
    title = "Create MyCompany"

class MyCompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = MyCompany
    form_class = MyCompanyForm
    template_name = "create.html"
    success_url = reverse_lazy('home:company')
    title = "Update MyCompany"

@login_required
def get_company(request):
    company = MyCompany.objects.first()
    return render(request, "company.html", {"company_detail": company, "title": "MyCompany"})


@login_required
def services_page(request):
    services = Service.objects.all()
    service_form = ServiceForm()
    context = {
        "services": services,
        "title": "Services",
        "service_form": service_form
    }

    if request.method == "POST":
        service_form = ServiceForm(request.POST, request.FILES)
        if service_form.is_valid():
            service_form.save()
            messages.success(request, "Service created successfully!")
            return redirect('home:services')
        else:
            messages.error(request, "Service creation failed!")
            return render(request, "service.html", context)
    return render(request, "service.html", context)


def faqs_page(request): 
    faqs = FAQ.objects.all()
    faq_form = FaqForm()
    if request.method == 'POST':
        faq_form = FaqForm(request.POST)
        if faq_form.is_valid():
            faq_form.save()
            return redirect('home:faqs')
    context = {
        "title": "FAQs",
        "faq_form": faq_form,
        "faqs": faqs,
    }
    return render(request, "faq.html", context)