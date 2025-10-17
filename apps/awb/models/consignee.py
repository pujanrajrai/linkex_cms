from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords

from .masters import DocumentType
from .awb import AWBDetail
from accounts.models import Country


class Consignee(BaseModel):
    history = HistoricalRecords()
    awb = models.OneToOneField(
        AWBDetail,
        on_delete=models.PROTECT,
        related_name="consignee"
    )
    company = models.CharField(max_length=255, null=True, blank=True)
    person_name = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    post_zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state_county = models.CharField(max_length=100, null=True, blank=True)
    state_abbreviation = models.CharField(
        max_length=100, null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=20, verbose_name="Phone Number 1")
    phone_number_2 = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Phone Number 2")
    email_address = models.EmailField(null=True, blank=True)
    document_type = models.ForeignKey(
        "DocumentType", on_delete=models.CASCADE, related_name="consignees", null=True, blank=True)
    document_number = models.CharField(max_length=100, null=True, blank=True)
    document_front = models.ImageField(
        upload_to="documents/fronts/", null=True, blank=True)
    document_back = models.ImageField(
        upload_to="documents/backs/", null=True, blank=True)

    class Meta:
        verbose_name = "Consignee / Receiver (TO)"
        verbose_name_plural = "Consignees / Receivers (TO)"

    def __str__(self):
        return f"{self.company} - {self.person_name}"
