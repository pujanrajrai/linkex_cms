# hscode/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from awb.models import HSCODE
from .forms import HSCODEForm

from django.utils.safestring import mark_safe
from django.db.models import Q
import json
import re
from django.http import HttpResponse, JsonResponse, QueryDict
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin'])
def hscode_list(request):
    hscodes = HSCODE.everything.all()
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        post_dict = QueryDict(request.POST.urlencode(), mutable=True)
        params_search = post_dict.get('columns')
        params_search_value = post_dict.get('search')
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)


        column_map = {
                0: None,
                1: 'description',
                2: 'code',
                3: 'search_key',
                4: None,
               
            }
        object_list = HSCODE.everything.all()

        count = object_list.count()

        search_value = request.POST.get('search[value]', '')
        if search_value:
            object_list = object_list.filter(
                Q(description__icontains=search_value) |
                Q(code__icontains=search_value) |
                Q(search_key__icontains=search_value)
            )


        order_idx = int(request.POST.get('order[0][column]', 1))
        order_dir = request.POST.get('order[0][dir]', 'desc')
        order_field = column_map.get(order_idx)
        if order_field:
            object_list = object_list.order_by(order_field if order_dir ==
                            'asc' else f'-{order_field}')
        else:
            object_list = object_list.order_by('-created_at')

        
        object_list = object_list[param_start:param_limit + param_start]
        filtered_total = object_list.count()
        row = list(object_list.values())

        context = {
            'draw': post_dict.get('draw'),
            'recordsTotal': count,
            'recordsFiltered': filtered_total,
            'data': row,
            "current": "hscode_master"
        }

        data = mark_safe(json.dumps(context, indent=4,
                         sort_keys=True, default=str))
        return HttpResponse(data, content_type='application/json')
    return render(request, 'awb/master/hscode/list.html', {"title": "HSCODE",})


@login_required
def get_hs_code(request):
    search_term = request.GET.get('query')
    result = HSCODE.objects.filter(
        Q(code__icontains=search_term) |
        Q(description__icontains=search_term) |
        Q(search_key__icontains=search_term)
    )
    data = [{'code': item.code, 'description': item.description}
            for item in result]
    return JsonResponse(data, safe=False)


@login_required
@has_roles(['admin'])
def hscode_create(request):
    form = HSCODEForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "HS Code created successfully!")
            return redirect('awb:pages:master:hscode:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "hscode_master", "title": "HSCODE",}
    return render(request, 'awb/master/hscode/create.html', context)


@login_required
@has_roles(['admin'])
def hscode_update(request, pk):
    hscode = get_object_or_404(HSCODE, pk=pk)
    form = HSCODEForm(request.POST or None, instance=hscode)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(request, "HS Code updated successfully!")
            return redirect('awb:pages:master:hscode:list')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {"form": form, "current": "hscode_master", "title": "HSCODE",}
    return render(request, 'awb/master/hscode/update.html', context)


@login_required
@has_roles(['admin'])
def hscode_delete(request):
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            hscode = get_object_or_404(HSCODE, pk=pk)
            hscode.delete()
            messages.success(request, "HS Code deleted successfully!")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:hscode:list"))
