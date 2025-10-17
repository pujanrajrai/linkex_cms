from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/export/', views.export_dashboard_data, name='export_dashboard'),
]
