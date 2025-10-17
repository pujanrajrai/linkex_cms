from django.urls import path, include
from . import views
app_name = 'courierx'
urlpatterns = [
    path('awb-courierx-api/', views.awb_courierx_api, name='awb_courierx_api'),
]
