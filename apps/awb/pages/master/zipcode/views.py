import pgeocode
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
import requests
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from accounts.models import ZipCode
from .forms import ZipCodeForm
from accounts.models import Country
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from django.utils.safestring import mark_safe
from django.db.models import Q
import json
import re
from decorators import has_roles
from django.contrib.auth.decorators import login_required

# from querystring_parser import parser


def get_zipcode_data(query, country_obj):
    """Retrieve zipcode data from the database or fetch from API if not found."""
    zip_entries = ZipCode.objects.filter(
        country=country_obj, postal_code=query)

    if zip_entries.exists():
        return [
            {
                'city': entry.city,
                'state': entry.state_county,
                'zip_code': entry.postal_code,
                'state_abbreviation': entry.state_abbreviation,
                'display_name': f"{entry.city}, {entry.state_county} ({entry.postal_code})"
            }
            for entry in zip_entries
        ]

    return fetch_and_store_zipcode(query, country_obj)


def fetch_and_store_zipcode(query, country_obj):
    country_code = country_obj.short_name.upper()
    raw_zip = str(query).strip().upper()
    results = []

    # Try pgeocode first
    nomi = pgeocode.Nominatim(country_code)
    loc = nomi.query_postal_code(raw_zip)

    if isinstance(loc.place_name, str) and loc.place_name:
        for city in loc.place_name.split(','):
            city = city.strip()
            results.append({
                'city': city,
                'state': loc.state_name,
                'zip_code': raw_zip,
                'state_abbreviation': loc.state_code,
                'display_name': f"{city}, {loc.state_name} ({raw_zip})"
            })

        return results

    # Fallback to Zippopotam API
    url = f"http://api.zippopotam.us/{country_code}/{raw_zip}"
    response = requests.get(url)

    if response.status_code != 200:
        return []  # No data found

    data = response.json()
    for item in data.get("places", []):
        city_name = item.get("place name", "").strip()
        state_name = item.get("state", "").strip()
        state_abbr = item.get("state abbreviation", "").strip()
        country_name = data.get("country", "").strip()

        if country_name.lower() == "canada":
            city_name = re.sub(r'\s*\(.*?\)', '', city_name).strip()

        results.append({
            'city': city_name,
            'state': state_name,
            'zip_code': raw_zip,
            'state_abbreviation': state_abbr,
            'display_name': f"{city_name}, {state_name} ({raw_zip})"
        })

        try:
            ZipCode.objects.get_or_create(
                country=country_obj,
                city=city_name,
                state_county=state_name,
                postal_code=raw_zip,
                state_abbreviation=state_abbr
            )
        except IntegrityError:
            continue  # Skip duplicate or invalid records

    return results


@csrf_exempt
def search_city(request):
    if request.method == 'GET':
        raw_country_name = request.GET.get('country', '').strip()
        country_name = raw_country_name.split('-')[1].strip()
        query = request.GET.get(
            'term', '').strip()

        if not query or not country_name:
            return JsonResponse([], safe=False)
        try:
            country_obj = Country.objects.get(name__iexact=country_name)
            results = get_zipcode_data(query, country_obj)
            return JsonResponse(results, safe=False)
        except Country.DoesNotExist:
            return JsonResponse([], safe=False)
        except Exception as e:
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)


@method_decorator(login_required, name='dispatch')
@method_decorator(has_roles(['admin']), name='dispatch')
class ZipCodeListView(ListView):
    """List all Zip Codes."""
    model = ZipCode
    template_name = "awb/master/zipcode/list.html"
    context_object_name = "zipcodes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current"] = "shipment_master"
        context["title"] = "Vendor"
        return context

    def post(self, request, *args, **kwargs):
        requested_html = re.search(
            r'^text/html', request.META.get('HTTP_ACCEPT'))
        if not requested_html:
            post_dict = QueryDict(request.POST.urlencode(), mutable=True)

            params_search = post_dict.get('columns')
            params_search_value = post_dict.get('search')
            param_start = max(int(request.POST.get('start', 0)), 0)
            param_limit = max(int(request.POST.get('length', 10)), 1)

            column_map = {
                0: None,
                1: 'country',
                2: 'city',
                3: 'state_county',
                4: 'postal_code',

            }

            object_list = self.model.objects.filter()

            count = self.model.objects.count()

            search_value = request.POST.get('search[value]', '')
            if search_value:
                object_list = object_list.filter(
                    Q(city__icontains=search_value) |
                    Q(state_county__icontains=search_value) |
                    Q(postal_code__icontains=search_value) |
                    Q(country__name__icontains=search_value)
                )
            filtered_total = object_list.count()

            order_idx = int(request.POST.get('order[0][column]', 1))
            order_dir = request.POST.get('order[0][dir]', 'desc')
            order_field = column_map.get(order_idx)
            if order_field:
                object_list = object_list.order_by(order_field if order_dir ==
                                                   'asc' else f'-{order_field}')
            else:
                object_list = object_list.order_by('-created_at')
            object_list = object_list[param_start:param_limit + param_start]
            row = list(object_list.values('id', 'country__name',
                       'city', 'state_county', 'postal_code'))

            context = {
                'draw': int(post_dict.get('draw', 1)),
                'recordsTotal': count,
                'recordsFiltered': filtered_total,
                'data': row,
            }

            data = mark_safe(json.dumps(context, indent=4,
                             sort_keys=True, default=str))
            return HttpResponse(data, content_type='application/json')

        return self.get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(has_roles(['admin']), name='dispatch')
class ZipCodeCreateView(CreateView):
    """Create a new Zip Code."""
    model = ZipCode
    form_class = ZipCodeForm
    template_name = "awb/master/zipcode/create.html"
    success_url = reverse_lazy("awb:pages:master:zipcode:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current"] = "shipment_master"
        context["title"] = "Vendor"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Zip Code created successfully!")
            return response
        except IntegrityError:
            messages.error(
                self.request, "Database Integrity Error: Possible duplicate entry or constraint violation.")
        except DatabaseError:
            messages.error(
                self.request, "Database error occurred while creating the zip code. Please try again later.")
        except ValidationError as e:
            messages.error(self.request, f"Validation Error: {str(e)}")
        except Exception as e:
            messages.error(
                self.request, f"An unexpected error occurred: {str(e)}")

        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(
            self.request, "Error creating zip code. Please check the form.")


@method_decorator(login_required, name='dispatch')
@method_decorator(has_roles(['admin']), name='dispatch')
class ZipCodeUpdateView(UpdateView):
    """Update an existing Zip Code."""
    model = ZipCode
    form_class = ZipCodeForm
    template_name = "awb/master/zipcode/update.html"
    success_url = reverse_lazy("awb:pages:master:zipcode:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current"] = "shipment_master"
        context["title"] = "Vendor"
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Zip Code updated successfully!")
            return response
        except IntegrityError:
            messages.error(
                self.request, "Database Integrity Error: Possible duplicate entry or constraint violation.")
        except DatabaseError:
            messages.error(
                self.request, "Database error occurred while updating the zip code. Please try again later.")
        except ValidationError as e:
            messages.error(self.request, f"Validation Error: {str(e)}")
        except Exception as e:
            messages.error(
                self.request, f"An unexpected error occurred: {str(e)}")

        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(
            self.request, "Error updating zip code. Please check the form.")
        return self.render_to_response(self.get_context_data(form=form))


@login_required
@has_roles(['admin'])
def zipcode_delete(request):
    """Delete a Zip Code."""
    if request.method == "POST":
        pk = request.POST.get("pk")
        try:
            zipcode = get_object_or_404(ZipCode, pk=pk)
            zipcode.delete()
            messages.success(request, "Zip Code deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting Zip Code: {str(e)}")

    return redirect(request.META.get("HTTP_REFERER", "awb:pages:master:zipcode:list"))
