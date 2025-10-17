from django.urls import path, include
from . import views
app_name = "awb"
urlpatterns = [

    path(
        'create', views.create_shipment_view, name="create"
    ),
    path(
        'update/<str:awb_no>/', views.update_shipment_view, name="update"
    ),
    path(
        'list', views.shipment_list, name="list"
    ),
    path('detail/<str:awb_no>/', views.shipment_detail, name='detail'),
    path('add/status/<str:awb_no>/', views.add_shipment_status, name='add_status'),
    path('delete/status/<int:status_id>/',
         views.delete_shipment_status, name='delete_status'),
    path('verify/<str:awb_no>/', views.verify_awb, name='verify'),
    path('unverify/<str:awb_no>/', views.unverify_awb, name='unverify'),
    path('print/<str:awb_no>/', views.print_awb, name='print'),
    path('print/label1/<str:awb_no>/',
         views.print_label1, name='print_label1'),
    path('print/box/label1/<str:awb_no>/',
         views.print_box_label1, name='print_box_label1'),
    path('print/ubx/label/<str:awb_no>/',
         views.print_ubx_label, name='print_ubx_label'),
    path('print/courierx/<str:awb_no>/',
         views.print_courierx_label, name='print_courierx_label'),
    path(
        'api/agencies/<str:pk>/', views.agency_detail, name='agency-api-detail'
    ),
    path('redirect/awb/', views.redirect_to_awb_detail, name='redirect_awb'),
    path('export/awb/<str:awb_no>/',
         views.export_awb_invoice_view, name='export_awb'),

    path('export/awb/box/<int:pk>/<str:mode>',
         views.export_awb_pdf, name='export_awb_pdf'),

    path('cancel/<str:awb_no>/', views.cancel_awb, name='cancel'),
    path('upload/forwarding/number/',
         views.upload_forwarding_number, name='upload_fwd_num'),
    path('history/<str:awb_no>/', views.shipment_history, name='shipment_history'),
    path('get/box/awb/no/<str:awb_no>/',
         views.get_box_awb_no, name='get_box_awb_no'),
    path('download/forwarding/number/template/',
         views.download_forwarding_number_template, name='download_fwd_num_template'),
    path('update/awb/numbers/',
         views.update_awb_numbers, name='update_awb_numbers'),
    path('get-country-code/',
         views.get_country_code, name='get_country_code'),

]
