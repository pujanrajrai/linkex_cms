from django.urls import path, include
from . import views


app_name = 'ledger'


urlpatterns = [
    path('list/', views.ledger_list, name='list'),
    path('create/', views.ledger_entry, name='create'),
    path('agency-balance/<int:agency_pk>/',
         views.get_agency_balance, name='agency-balance'),
    path('export-excel/', views.ExportLedgerExcel.as_view(), name='export_excel'),

]
