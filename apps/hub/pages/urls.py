from django.urls import path, include


app_name = 'pages'
urlpatterns = [
    path('hub/', include('hub.pages.hub.urls')),
    path('run/', include('hub.pages.run.urls')),
]
