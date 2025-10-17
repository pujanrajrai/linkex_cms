# product_type/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from awb.models import ProductType
from .forms import ProductTypeForm
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def product_type_list(request):
    product_types = ProductType.everything.all()
    context = {"product_types": product_types,
               "current": "product_type_master", "title": "ProductType",}
    return render(request, 'awb/master/product_type/list.html', context)


@login_required
@has_roles(['admin'])
def product_type_create(request):
    form = ProductTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Product Type created successfully!")
            return redirect('awb:pages:master:product_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "product_type_master", "title": "ProductType",}
    return render(request, 'awb/master/product_type/create.html', context)


@login_required
@has_roles(['admin'])
def product_type_update(request, pk):
    product_type = get_object_or_404(ProductType, pk=pk)
    form = ProductTypeForm(request.POST or None, instance=product_type)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "Product Type updated successfully!")
            return redirect('awb:pages:master:product_type:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "product_type_master", "title": "ProductType",}
    return render(request, 'awb/master/product_type/update.html', context)


@login_required
@has_roles(['admin'])
def product_type_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            product_type = get_object_or_404(ProductType, pk=pk)
            product_type.delete()
            messages.success(request, "Product Type deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:product_type:list"))





@login_required
@has_roles(['admin', 'agencyuser'])
def get_product_type_with_vendor(request, vendor_pk):
    try:
        product_types = ProductType.objects.filter(vendor__pk=vendor_pk)
        data = [{'id': pt.id, 'name': pt.name} for pt in product_types]
        return JsonResponse(data, safe=False)
    except:
        return JsonResponse([], safe=False)
