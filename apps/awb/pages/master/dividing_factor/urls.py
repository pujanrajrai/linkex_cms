# dividing_factor/urls.py
from django.urls import path
from . import views

app_name = 'dividing_factor'

urlpatterns = [
    path('', views.dividing_factor_list, name='list'),
    path('create/', views.dividing_factor_create, name='create'),
    path('update/<str:pk>/', views.dividing_factor_update, name='update'),
    path('delete/', views.dividing_factor_delete, name='delete'),
]
