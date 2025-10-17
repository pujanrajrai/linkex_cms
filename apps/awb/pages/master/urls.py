from django.urls import path, include

app_name = "master"


urlpatterns = [
    path('company/', include('awb.pages.master.company.urls')),
    path('country/', include('awb.pages.master.country.urls')),
    path('currency/', include('awb.pages.master.currency.urls')),
    path('document_type/', include('awb.pages.master.document_type.urls')),
    path('zipcode/', include('awb.pages.master.zipcode.urls')),
    path('hscode/', include('awb.pages.master.hscode.urls')),
    path('unit_type/', include('awb.pages.master.unit_type.urls')),
    path('vendor/', include('awb.pages.master.vendor.urls')),
    path('product_type/', include('awb.pages.master.product_type.urls')),
    path('service/', include('awb.pages.master.service.urls')),
    path('manifest/', include('awb.pages.master.manifest.urls')),
    path('dividing_factor/', include('awb.pages.master.dividing_factor.urls')),

]
