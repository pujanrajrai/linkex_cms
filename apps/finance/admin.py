from django.contrib import admin
from .models.invoice import Invoice, Ledger

admin.site.register(Invoice)
admin.site.register(Ledger)

# Register your models here.
