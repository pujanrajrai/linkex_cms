from django.db import models, transaction
from django.db.models import Max
from django.db import models
from base.models import BaseModel
from .masters import Country
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _


class Module(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class AgencyRequest(BaseModel):
    history = HistoricalRecords()
    company_name = models.CharField(
        max_length=255,
        unique=True,
    )
    logo = models.ImageField(
        upload_to='agency_logo',
        null=True,
        blank=True
    )
    owner_name = models.CharField(
        max_length=255
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT
    )

    address1 = models.CharField(
        max_length=200
    )
    address2 = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    zip_code = models.CharField(
        max_length=10
    )
    state = models.CharField(
        max_length=100
    )
    city = models.CharField(
        max_length=100
    )
    email = models.EmailField(
        max_length=255,
    )
    contact_no_1 = models.CharField(
        max_length=20,
        help_text="Contact number 1"
    )
    contact_no_2 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Contact number 2"
    )

    company_pan_vat = models.FileField(
        upload_to='company_pan_vat',
        null=True,
        blank=True
    )
    citizenship_front = models.FileField(
        upload_to='citizenship_front',
        null=True,
        blank=True
    )
    citizenship_back = models.FileField(
        upload_to='citizenship_back',
        null=True,
        blank=True
    )
    passport = models.FileField(
        upload_to='passport',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Agency(BaseModel):
    history = HistoricalRecords()
    company_name = models.CharField(
        max_length=255,
        unique=True,
    )
    logo = models.ImageField(
        upload_to='agency_logo',
        null=True,
        blank=True
    )
    owner_name = models.CharField(
        max_length=255
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT
    )

    address1 = models.CharField(
        max_length=200
    )
    address2 = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    zip_code = models.CharField(
        max_length=10
    )
    state = models.CharField(
        max_length=100
    )
    city = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        max_length=255,
    )
    contact_no_1 = models.CharField(
        max_length=20,
    )
    contact_no_2 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    max_user = models.PositiveIntegerField(
        default=0
    )
    is_blocked = models.BooleanField(
        default=False
    )
    agency_code = models.PositiveIntegerField(
        unique=True,
        editable=False
    )

    custom_per_kg_rate = models.FloatField(
        default=0
    )
    handling_per_box_rate = models.FloatField(
        default=0
    )
    company_pan_vat = models.FileField(
        upload_to='company_pan_vat',
        null=True,
        blank=True
    )
    citizenship_front = models.FileField(
        upload_to='citizenship_front',
        null=True,
        blank=True
    )
    citizenship_back = models.FileField(
        upload_to='citizenship_back',
        null=True,
        blank=True
    )
    passport = models.FileField(
        upload_to='passport',
        null=True,
        blank=True
    )
    can_verify_awb = models.BooleanField(
        default=False
    )
    can_call_api = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        # Only generate a new agency_code if it's not set (i.e., on creation).
        if not self.agency_code:
            with transaction.atomic():
                last_code = Agency.objects.aggregate(max_code=Max('agency_code'))[
                    'max_code'] or 110
                self.agency_code = last_code + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


class AgencyAccess(BaseModel):
    history = HistoricalRecords()
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='agency_accesses'
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='agency_accesses'
    )
    can_create = models.BooleanField(
        default=False
    )
    can_view = models.BooleanField(
        default=False
    )
    can_update = models.BooleanField(
        default=False
    )
    can_delete = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = (
            'agency',
            'module',
        )

    def __str__(self):
        return f"{self.agency.company_name} - {self.module.name}"
