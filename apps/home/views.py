from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


from .models import MyCompany, Service, FAQ, ProhibitedItems
from .forms import MyCompanyForm, ServiceForm, FaqForm, ProhibitedItemForm
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



@login_required
def service_delete(request, pk):
    service = Service.objects.get(pk=pk)
    service.delete()
    messages.success(request, "Service deleted successfully!")
    return redirect('home:services')


@login_required
def service_update(request, pk):
    service = Service.objects.get(pk=pk)
    service_form = ServiceForm(instance=service)
    if request.method == 'POST':
        service_form = ServiceForm(request.POST, request.FILES, instance=service)
        if service_form.is_valid():
            service_form.save()
            messages.success(request, "Service updated successfully!")
            return redirect('home:services')
        else:
            messages.error(request, "Service update failed!")
            return render(request, "service.html", context)
    context = {
        "title": "Services",
        "service_form": service_form,
        "service": service,
    }
    return render(request, "service.html", context)




@login_required
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


@login_required
def faq_delete(request, pk):
    faq = FAQ.objects.get(pk=pk)
    faq.delete()
    messages.success(request, "FAQ deleted successfully!")
    return redirect('home:faqs')


@login_required
def faq_update(request, pk):
    faq = FAQ.objects.get(pk=pk)
    faq_form = FaqForm(instance=faq)
    if request.method == 'POST':
        faq_form = FaqForm(request.POST, instance=faq)      
        if faq_form.is_valid():
            faq_form.save()
            messages.success(request, "FAQ updated successfully!")
            return redirect('home:faqs')
        else:
            messages.error(request, "FAQ update failed!")
            return render(request, "faq.html", context)
    context = {
        "title": "FAQs",
        "faq_form": faq_form,
        "faq": faq,
    }       
    return render(request, "faq.html", context)



@login_required
def prohibited_items_page(request):
    prohibited_items = ProhibitedItems.objects.all()
    form = ProhibitedItemForm()
    if request.method == 'POST':
        form = ProhibitedItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:prohibited_items')
    context = {
        "title": "Prohibited Items",
        "prohibited_items": prohibited_items,   
        "form": form,
    }
    return render(request, "prohibited_items.html", context)


@login_required
def prohibited_item_delete(request, pk):
    prohibited_item = ProhibitedItems.objects.get(pk=pk)
    prohibited_item.delete()
    messages.success(request, "Prohibited item deleted successfully!")
    return redirect('home:prohibited_items')

@login_required
def prohibited_item_update(request, pk):
    prohibited_item = ProhibitedItems.objects.get(pk=pk)
    form = ProhibitedItemForm(instance=prohibited_item) 
    if request.method == 'POST':
        form = ProhibitedItemForm(request.POST, instance=prohibited_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Prohibited item updated successfully!")
            return redirect('home:prohibited_items')
        else:
            messages.error(request, "Prohibited item update failed!")
            return render(request, "prohibited_items.html", context)
    context = {
        "title": "Prohibited Items",
        "form": form,
        "prohibited_item": prohibited_item,
    }
    return render(request, "prohibited_items.html", context)