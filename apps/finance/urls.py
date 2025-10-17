from django.urls import path, include


app_name = 'finance'

urlpatterns = [
    path('pages/', include('finance.pages.urls')),
]
