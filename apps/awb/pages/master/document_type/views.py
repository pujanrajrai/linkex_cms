from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from awb.models import DocumentType
from .forms import DocumentTypeForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def document_type_list(request):
    document_types = DocumentType.everything.all()
    context = {"document_types": document_types, "current": "shipment_master", "title": "DocumentType",}
    return render(request, 'awb/master/document_type/list.html', context)


@login_required
@has_roles(['admin'])
def document_type_create(request):
    form = DocumentTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Document type created successfully!")
            return redirect('awb:pages:master:document_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "DocumentType",}
    return render(request, 'awb/master/document_type/create.html', context)


@login_required
@has_roles(['admin'])
def document_type_update(request, pk):
    document_type = get_object_or_404(DocumentType, pk=pk)
    form = DocumentTypeForm(request.POST or None, instance=document_type)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Document type updated successfully!")
            return redirect('awb:pages:master:document_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "shipment_master", "title": "DocumentType",}
    return render(request, 'awb/master/document_type/update.html', context)


@login_required
@has_roles(['admin'])
def document_type_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            document_type = get_object_or_404(DocumentType, pk=pk)
            document_type.delete()
            messages.success(request, "Document type deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:document_type:list"))
