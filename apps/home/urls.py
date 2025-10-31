from django.urls import path, include
from .views import *
app_name = 'home'

urlpatterns = [
    path('create/', MyCompanyCreateView.as_view(), name="company_create"),
    path('update/<int:pk>', MyCompanyUpdateView.as_view(), name="company_update"),
    path('', get_company, name="company"),
    path('services/', services_page, name="services"),
    path('service/update/<int:pk>', service_update, name="service_update"),
    path('service/delete/<int:pk>', service_delete, name="service_delete"),
    path('faqs/', faqs_page, name="faqs"),
    path('faq/update/<int:pk>', faq_update, name="faq_update"),
    path('faq/delete/<int:pk>', faq_delete, name="faq_delete"),


    path('prohibited-items/', prohibited_items_page, name="prohibited_items"),
    path('prohibited-item/delete/<int:pk>', prohibited_item_delete, name="prohibited_item_delete"),
    path('prohibited-item/update/<int:pk>', prohibited_item_update, name="prohibited_item_update"),
]
