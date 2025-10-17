# service/urls.py
from django.urls import path
from . import views

app_name = 'service'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('create/', views.service_create, name='create'),
    path('update/<str:pk>/', views.service_update, name='update'),
    path('delete/', views.service_delete, name='delete'),

    path('get/service/<int:vendor_pk>/', views.get_services_with_vendor, name='get_services_with_vendor')
]
