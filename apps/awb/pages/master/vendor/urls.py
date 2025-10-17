# unit_type/urls.py
from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('', views.vendor_list, name='list'),
    path('create/', views.vendor_create, name='create'),
    path('update/<str:pk>/', views.vendor_update, name='update'),
    path('delete/', views.vendor_delete, name='delete'),
]
