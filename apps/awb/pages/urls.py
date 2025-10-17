from django.urls import path, include

app_name = "pages"


urlpatterns = [
    path('awb/', include('awb.pages.awb.urls')),
    path('master/', include('awb.pages.master.urls')),
    path('pickup-request/', include('awb.pages.pickup_request.urls')),
    path('awb-api-responses/', include('awb.pages.awb_apiresponses.urls')),
    path('invoice/', include('awb.pages.invoice.urls')),
    path('report/', include('awb.pages.report.urls')),

]
