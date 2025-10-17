from django.urls import path
from . import views

app_name = 'pickup_request'

urlpatterns = [
    path('create/', views.create_pickup_request, name='create'),
    path('list/', views.pickup_request_list, name='list'),  
    path('update/<str:pk>/', views.pickup_request_update, name='update'),
    path('delete/', views.pickup_request_delete, name='delete'),
    path('status-update/<str:pk>/', views.pickup_request_status_update, name='status_update'),
]
