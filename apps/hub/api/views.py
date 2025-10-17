from django.http import JsonResponse
from awb.models import AWBDetail
from django.db.models import Prefetch
from awb.models import BoxDetails
from django.views.decorators.http import require_POST
import json
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def get_awbs(request):
    company_id = request.GET.get('company')
    hub_id = request.GET.get('hub')

    if not company_id or not hub_id:
        return JsonResponse({'error': 'Company and hub are required'}, status=400)

    # Get AWBs with their boxes
    awbs = AWBDetail.objects.filter(
        company_id=company_id,
        hub_id=hub_id,
        is_deleted=False
    ).prefetch_related(
        Prefetch('boxdetails_set',
                 queryset=BoxDetails.objects.filter(is_deleted=False))
    ).select_related('origin', 'destination')

    # Format the response
    awb_list = []
    for awb in awbs:
        boxes = []
        for box in awb.boxdetails_set.all():
            box_data = {
                'id': box.id,
                'actual_weight': box.actual_weight,
                'volumetric_weight': box.volumetric_weight,
                'charged_weight': box.charged_weight,
                'dimensions': f"{box.length}x{box.breadth}x{box.height}",
                'length': box.length,
                'breadth': box.breadth,
                'height': box.height,
                'display_text': f"Box #{box.id} - {box.actual_weight}kg ({box.length}x{box.breadth}x{box.height}cm)"
            }
            boxes.append(box_data)

        awb_list.append({
            'id': awb.id,
            'awbno': awb.awbno,
            'origin': str(awb.origin),
            'destination': str(awb.destination),
            'boxes': boxes,
            'total_boxes': len(boxes)
        })

    return JsonResponse(awb_list, safe=False)


@login_required
@has_roles(['admin'])
@require_POST
def filter_awbs(request):
    """
    API endpoint to filter AWBs based on company and hub
    Returns AWBs that are not already in any run
    """
    try:
        data = json.loads(request.body)
        companies = data.get('companies', [])
        hubs = data.get('hubs', [])

        # Base query - only get AWBs that are not in any run
        query = AWBDetail.objects.filter(
            is_in_run=False).select_related('company')

        # Apply company filter if provided
        if companies:
            query = query.filter(company__id__in=companies)

        # Apply hub filter if provided
        if hubs:
            query = query.filter(hub__id__in=hubs)

        # Format results
        results = [
            {
                'id': awb.id,
                'awbno': awb.awbno,
                'company_name': awb.company.name if hasattr(awb, 'company') and awb.company else '',
                'total_box': getattr(awb, 'total_box', 0),
                'actual_weight': float(awb.total_actual_weight) if hasattr(awb, 'total_actual_weight') and awb.total_actual_weight else 0,
                'volumetric_weight': float(awb.total_volumetric_weight) if hasattr(awb, 'total_volumetric_weight') and awb.total_volumetric_weight else 0,
                'charged_weight': float(awb.total_charged_weight) if hasattr(awb, 'total_charged_weight') and awb.total_charged_weight else 0
            }
            for awb in query
        ]

        return JsonResponse({'awbs': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
