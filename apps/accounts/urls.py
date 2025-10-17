from django.urls import path, include
app_name = "accounts"
urlpatterns = [
    path('pages/', include('accounts.pages.urls'))
]
