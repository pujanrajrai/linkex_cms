from django.urls import path, include
from . import views
app_name = 'ubx'
urlpatterns = [
    path('awb-ubx-api/', views.awb_ubx_api, name='awb_ubx_api'),

]
