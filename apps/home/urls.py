from django.urls import path, include
from .views import MyCompanyUpdateView, MyCompanyCreateView, get_company, services_page, faqs_page

app_name = 'home'

urlpatterns = [
    path('create/', MyCompanyCreateView.as_view(), name="company_create"),
    path('update/<int:pk>', MyCompanyUpdateView.as_view(), name="company_update"),
    path('', get_company, name="company"),
    path('services/', services_page, name="services"),
    path('faqs/', faqs_page, name="faqs"),
]
