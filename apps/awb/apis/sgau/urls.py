from django.urls import path, include
from . import views
app_name = 'sgau'
urlpatterns = [
    path('awb-sgau-api/', views.awb_sgau_api, name='awb_sgau_api'),
]
