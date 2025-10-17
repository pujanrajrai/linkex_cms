from awb.apis.utils import track_awb
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from awb.models import AWBDetail


@login_required
def tracking_awb(request):
    awb_no = request.GET.get('awbno')
    result = track_awb(awb_no)
    return JsonResponse(result)
