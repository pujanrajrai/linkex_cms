from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords

from .masters import DocumentType
from .awb import AWBDetail
from accounts.models import Country


class Consignor(BaseModel):
    history = HistoricalRecords()
    awb = models.OneToOneField(
        AWBDetail,
        on_delete=models.PROTECT,
        related_name="consignor"
    )
    company = models.CharField(max_length=255)
    person_name = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    post_zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state_county = models.CharField(max_length=100, null=True, blank=True)
    
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField(null=True, blank=True)
    document_type = models.ForeignKey(
        DocumentType, on_delete=models.CASCADE, related_name="consignors", null=True, blank=True)
    document_number = models.CharField(
        max_length=100, null=True, blank=True)
    document_front = models.ImageField(
        upload_to="documents/fronts/", null=True, blank=True)
    document_back = models.ImageField(
        upload_to="documents/backs/", null=True, blank=True)

    class Meta:
        verbose_name = "Shipper / Consignor (FROM)"
        verbose_name_plural = "Shippers / Consignors (FROM)"

    def __str__(self):
        return f"{self.company} - {self.person_name}"
