from random import choice
from django.db import models
from simple_history.models import HistoricalRecords


from base.models import BaseModel
from accounts.models import Currency, Country


class CurrencyChoices(models.TextChoices):
    NPR = 'NPR'
    USD = 'USD'


class ManifestFormat(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100, unique=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.display_name


class Vendor(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=100, unique=True)
    account_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    manifest_format = models.ManyToManyField(
        ManifestFormat,
        related_name='vendor_manifest_format'
    )
    priority = models.IntegerField(default=0)
    code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    legal_name = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    address1 = models.CharField(max_length=100, null=True, blank=True)
    address2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = f"VENDOR-{self.id}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return f"{self.name} ({self.account_number or ''})"


class Hub(BaseModel):

    history = HistoricalRecords()
    hub_code = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT
    )
    city = models.CharField(max_length=100, null=True, blank=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT
    )

    vendor = models.ManyToManyField(
        Vendor,
        related_name='hub_vendor'
    )
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return self.name
