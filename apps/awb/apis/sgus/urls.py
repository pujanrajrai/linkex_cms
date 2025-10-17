from django.urls import path, include
from . import views
app_name = 'sgus'
urlpatterns = [
    path('awb-sgus-api/', views.awb_sgus_api, name='awb_sgus_api'),
]
