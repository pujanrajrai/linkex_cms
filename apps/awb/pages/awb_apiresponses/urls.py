from django.urls import path
from . import views

app_name = 'awb_apiresponses'

urlpatterns = [
    path('list/', views.api_responses_list, name='list'),
    path('export/', views.export_api_responses, name='export'),
]
