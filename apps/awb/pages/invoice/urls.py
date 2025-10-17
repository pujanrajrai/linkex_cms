from django.urls import path
from . import views

app_name = 'invoice'

urlpatterns = [
    path('list/<str:awb_no>/', views.invoice_list, name='list'),
    path('create/<str:awb_no>/', views.create_invoice, name='create'),
    path('print/<str:awb_no>/<int:invoice_id>/',
         views.print_invoice, name='print'),
    path('cancel/<str:awb_no>/<int:invoice_id>/',
         views.cancel_invoice, name='cancel'),
]
