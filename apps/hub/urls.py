from django.urls import path, include

app_name = 'hub'
urlpatterns = [
    path('pages/', include('hub.pages.urls')),
    path('api/', include('hub.api.urls')),
]
