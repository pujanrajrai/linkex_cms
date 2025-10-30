from django.urls import path, include
from .views import CompanyUpdateView, CompanyCreateView, get_company

app_name = 'home'

urlpatterns = [
    path('create/', CompanyCreateView.as_view(), name="company_create"),
    path('update/<int:pk>', CompanyUpdateView.as_view(), name="company_update"),
    path('', get_company, name="company"),
]
