from django.urls import path, include
from . import views
app_name = 'dtdc'
urlpatterns = [
    path('awb-dtdc-api/', views.awb_dtdc_api, name='awb_dtdc_api'),
]
