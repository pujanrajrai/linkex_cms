from hub.models.hub import Vendor
from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords


class DocumentType(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class HSCODE(BaseModel):
    history = HistoricalRecords()
    history = HistoricalRecords()

    description = models.CharField(
        max_length=255,
        unique=True
    )
    code = models.CharField(
        max_length=100
    )
    search_key = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.description


class UnitType(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=50, unique=True,
                            help_text="Type of unit (e.g., kg, pcs, meter)")
    priority = models.IntegerField(default=0)
    vendor = models.ManyToManyField(
        Vendor,
        related_name='unit_type_vendor'
    )

    class Meta:
        verbose_name = "Unit Type"
        verbose_name_plural = "Unit Types"
        ordering = ['-priority']

    def __str__(self):
        return self.name


class ProductType(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    vendor = models.ManyToManyField(
        Vendor,
        related_name='product_type_vendor'
    )

    class Meta:
        constraints = [
            # Ensuring that only one ProductType can be marked as default
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_product_type'
            )
        ]

    def __str__(self):
        return self.name


class Service(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    product_code = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    vendor = models.ManyToManyField(
        Vendor,
        related_name='service_vendor'
    )

    def __str__(self):
        return self.name
