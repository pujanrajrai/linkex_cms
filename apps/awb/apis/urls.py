from django.urls import path, include
from . import views
app_name = 'apis'
urlpatterns = [
    path('tracking-awb/', views.tracking_awb, name='tracking_awb'),
    path('dtdc/', include('awb.apis.dtdc.urls', namespace='dtdc')),
    path('sgau/', include('awb.apis.sgau.urls', namespace='sgau')),
    path('sgus/', include('awb.apis.sgus.urls', namespace='sgus')),
    path('sgca/', include('awb.apis.sgca.urls', namespace='sgca')),
    path('courierx/', include('awb.apis.courierx.urls', namespace='courierx')),
    path('ubx/', include('awb.apis.ubx.urls', namespace='ubx')),
]
