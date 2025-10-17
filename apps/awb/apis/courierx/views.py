from django.http import JsonResponse
from awb.apis.courierx.utils import couriex_api
from decorators import has_roles
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


@login_required
@has_roles(['admin', 'agencyuser'])
def awb_courierx_api(request):
    awb_no = request.GET.get('awbno')
    role = request.user.role
    if role == 'agencyuser':
        agency = request.user.agency
        if not agency.can_call_api:
            return JsonResponse({
                "success": False,
                "awbno": awb_no,
                "message": "You don't have permission to call this API.",
                "data": None
            })
    result = couriex_api(awb_no)
    return JsonResponse(result)
