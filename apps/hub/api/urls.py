from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_awbs, name='get_awbs'),
    path('filter-awbs/', views.filter_awbs, name='filter_awbs'),
]
