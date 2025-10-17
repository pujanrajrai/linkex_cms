from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib import messages
from finance.models import Invoice
from awb.models.awb import AWBDetail
from awb.pages.invoice.forms import InvoiceForm
from decorators import has_roles


@login_required
@has_roles(['admin', 'agencyuser'])
def invoice_list(request, awb_no):
    awb = get_object_or_404(AWBDetail, awbno=awb_no)
    invoices = Invoice.objects.filter(awb=awb).order_by('-created_at')

    # Get consignor and consignee (they should exist due to OneToOne relationship)
    try:
        consignor = awb.consignor
    except:
        consignor = None

    try:
        consignee = awb.consignee
    except:
        consignee = None

    context = {
        'awb': awb,
        'invoices': invoices,
        'consignor': consignor,
        'consignee': consignee,
        'title': f'Invoice List - AWB {awb_no}',
        'active_tab': 'invoice'
    }
    return render(request, 'awb/invoice/invoice_list.html', context)


@login_required
@has_roles(['admin'])
def create_invoice(request, awb_no):
    awb = get_object_or_404(AWBDetail, awbno=awb_no)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES, awb=awb)
        if form.is_valid():
            try:
                invoice = form.save(commit=False)
                invoice.awb = awb
                invoice.save()
                messages.success(request, 'Invoice created successfully!')
                return redirect('awb:pages:invoice:list', awb_no=awb_no)
            except ValidationError as e:
                messages.error(request, e.message)
    else:
        form = InvoiceForm(awb=awb)

    context = {
        'form': form,
        'title': f'Create Invoice - AWB {awb_no}',
        'awb': awb,
        'active_tab': 'invoice'
    }
    return render(request, 'awb/invoice/create.html', context)


@login_required
@has_roles(['admin'])
def print_invoice(request, awb_no, invoice_id):
    """Print invoice view"""
    awb = get_object_or_404(AWBDetail, awbno=awb_no)
    invoice = get_object_or_404(Invoice, id=invoice_id, awb=awb)

    context = {
        'invoice': invoice,
        'awb': awb,
        'title': f'Print Invoice #{invoice.id} - AWB {awb_no}'
    }
    return render(request, 'awb/invoice/print.html', context)


@login_required
@has_roles(['admin'])
def cancel_invoice(request, awb_no, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, awb__awbno=awb_no)
    invoice.is_active = False
    invoice.save()
    messages.success(
        request, f'Invoice #{invoice.id} has been cancelled successfully!')
    # return to the same page
    return redirect(request.META.get('HTTP_REFERER'))
