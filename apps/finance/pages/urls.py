from django.urls import path, include


app_name = 'pages'

urlpatterns = [
    path('invoice/', include('finance.pages.invoice.urls')),
    path('payment/', include('finance.pages.payment.urls')),
    path('ledger/', include('finance.pages.ledger.urls')),
]
