from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages


from decorators import has_roles
from finance.models import Invoice
from .form import InvoiceForm
from awb.models import AWBDetail



@login_required
@has_roles(['admin'])
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'finance/invoice/list.html', {'invoices': invoices})



@login_required
@has_roles(['admin'])
def invoice_create(request, awb_no):
    awb = get_object_or_404(AWBDetail, awbno=awb_no)
    form = InvoiceForm(request.POST or None, awb_no=awb_no)
    if form.is_valid():
        form.save()
        messages.success(request, 'Invoice created successfully')
        return redirect('finance:pages:invoice:list')
    return render(request, 'finance/invoice/create.html', {'form': form})



@login_required
@has_roles(['admin'])
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.save()
        messages.success(request, 'Invoice updated successfully')
        return redirect('finance:pages:invoice:list')
    return render(request, 'finance/invoice/update.html', {'form': form})
