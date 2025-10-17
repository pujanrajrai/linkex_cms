from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.contrib import messages
from django.db import models


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # maximum number of items per page

    def get_page_size(self, request):
        data = request.GET.copy()
        page_size = data.get('page_size', None)

        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size < 1:
                    return self.page_size
                elif page_size > self.max_page_size:
                    return self.max_page_size
                else:
                    return page_size
            except ValueError:
                pass
        return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'count': self.page.paginator.count,
            'data': data,
        })



def process_string_fields(instance, exclude_fields=None):
    """
    Process all string fields (CharField and TextField) in a model instance
    and convert them to uppercase except for excluded fields.
    
    Args:
        instance: Model instance to process
        exclude_fields: Set of field names to exclude from uppercase conversion
    
    Returns:
        None (modifies the instance in place)
    """
    if exclude_fields is None:
        exclude_fields = set()
    
    # Get all fields from the model
    for field in instance._meta.fields:
        # Check if it's a string field and not in exclude_fields
        if (isinstance(field, (models.CharField, models.TextField)) and 
            field.name not in exclude_fields):
            # Get the current value
            value = getattr(instance, field.name)
            # Convert to uppercase if it's a string
            if value is not None and isinstance(value, str):
                setattr(instance, field.name, value.upper()) 

