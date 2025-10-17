from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from awb.models import PickupRequest
from awb.pages.pickup_request.forms import PickupRequestForm, PickupStatusUpdateForm
from decorators import has_roles

@login_required
@has_roles(['admin', 'agencyuser'])
def create_pickup_request(request):
    if request.method == 'POST':
        form = PickupRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pickup request created successfully')
            return redirect('awb:pages:pickup_request:list')
    else:
        form = PickupRequestForm()
    return render(request, 'awb/pickup_request/create.html', {'form': form})



@login_required
@has_roles(['admin', 'agencyuser'])
def pickup_request_list(request):
    pickup_requests = PickupRequest.objects.all()
    if request.user.role == 'agencyuser':
        pickup_requests = pickup_requests.filter(agency=request.user.agency)
    return render(request, 'awb/pickup_request/list.html', {'pickup_requests': pickup_requests})



@login_required
@has_roles(['admin', 'agencyuser'])
def pickup_request_update(request, pk):
    pickup_request = PickupRequest.objects.get(pk=pk)
    form = PickupRequestForm(request.POST or None, instance=pickup_request)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Pickup request updated successfully')
        return redirect('awb:pages:pickup_request:list')
    return render(request, 'awb/pickup_request/update.html', {'form': form})


@login_required
@has_roles(['admin', 'agencyuser'])
def pickup_request_delete(request):
    if request.user.role == 'agencyuser':
        if not request.user.is_default_user or request.user.agency.id != PickupRequest.objects.get(pk=request.POST.get("pk")).agency.id:
            messages.error(request, 'You are not authorized to delete this pickup request')
            return redirect('awb:pages:pickup_request:list')
    if request.method == 'POST':
        pk = request.POST.get("pk")
        PickupRequest.objects.get(pk=pk).delete()
        messages.success(request, 'Pickup request deleted successfully')
        return redirect('awb:pages:pickup_request:list')
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:pickup_request:list"))



@login_required
@require_POST
@has_roles(['admin'])
def pickup_request_status_update(request, pk):
    pickup_request = PickupRequest.objects.get(pk=pk)
    form = PickupStatusUpdateForm(request.POST, instance=pickup_request)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pickup request status updated successfully')
        return redirect('awb:pages:pickup_request:list')
    messages.error(request, 'Invalid form data')
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:pickup_request:list"))
