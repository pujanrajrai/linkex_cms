# product_type/urls.py
from django.urls import path
from . import views

app_name = 'product_type'

urlpatterns = [
    path('', views.product_type_list, name='list'),
    path('create/', views.product_type_create, name='create'),
    path('update/<str:pk>/', views.product_type_update, name='update'),
    path('delete/', views.product_type_delete, name='delete'),

    path('get/product-type/<int:vendor_pk>/', views.get_product_type_with_vendor, name='get_product_type')
]
