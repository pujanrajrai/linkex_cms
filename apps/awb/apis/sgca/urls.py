from django.urls import path, include
from . import views
app_name = 'sgca'
urlpatterns = [
    path('awb-sgca-api/', views.awb_sgca_api, name='awb_sgca_api'),
]
