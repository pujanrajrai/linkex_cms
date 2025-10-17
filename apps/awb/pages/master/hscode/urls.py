# hscode/urls.py
from django.urls import path
from . import views

app_name = 'hscode'

urlpatterns = [
    path('', views.hscode_list, name='list'),
    path('create/', views.hscode_create, name='create'),
    path('update/<str:pk>/', views.hscode_update, name='update'),
    path('delete/', views.hscode_delete, name='delete'),
    path('get-hscode/', views.get_hs_code, name='search_hscode')
]
