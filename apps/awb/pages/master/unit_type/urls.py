# unit_type/urls.py
from django.urls import path
from . import views

app_name = 'unit_type'

urlpatterns = [
    path('', views.unit_type_list, name='list'),
    path('create/', views.unit_type_create, name='create'),
    path('update/<str:pk>/', views.unit_type_update, name='update'),
    path('delete/', views.unit_type_delete, name='delete'),
    path('get-vendor-unit-type/<str:vendor_pk>/',
         views.get_vendor_unit_type, name='get_vendor_unit_type'),
]
