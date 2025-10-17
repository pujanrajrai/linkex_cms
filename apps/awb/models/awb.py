import xml.etree.ElementTree as ET
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords
from .masters import ProductType, Service
from accounts.models import Agency, Company, Country, Currency, DividingFactor
from hub.models import Hub, Vendor
from django.db.models import Sum
import math
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile


status_choices = [
    ('LABEL CREATED', 'Label created'),
    ('SHIPMENT BOOKED', 'Shipment Booked'),
    ('SHIPMENT PICKED UP', 'Shipment Picked Up'),
    ('PROCESSED AT', 'Processed At'),
    ('DEPARTED FACILITY IN', 'Departed Facility In'),
    ('ON THE WAY', 'On the way'),
    ('ARRIVED AT SORT FACILITY', 'Arrived At Sort Facility'),
    ('ARRIVED AT DESTINATION', 'Arrived At Destination'),
    ('CUSTOMS STATUS UPDATED', 'Customs Status Updated'),
    ('CLEARANCE DELAY - IMPORT', 'Clearance delay - Import'),
    ('CLEARANCE IN PROGRESS', 'Clearance in progress'),
    ('CLEARANCE PROCESSING COMPLETE AT', 'Clearance Processing Complete At'),
    ('RECEIVED AT HUB', 'Received At Hub'),
    ('AT PARCEL DELIVERY CENTER', 'At parcel delivery center'),
    ('OUT FOR DELIVERY', 'Out for Delivery'),
    ('SHIPMENT ON HOLD', 'Shipment on Hold'),
    ('CANCELLED', 'Cancelled'),
    ('RETURNING PACKAGE TO SHIPPER', 'Returning package to shipper'),
    ('DELIVERED', 'Delivered'),
]

reason_for_export_choices = [
    ('COMMERCIAL', 'COMMERCIAL'),
    ('GIFT', 'GIFT'),
    ('PERSONAL NOT FOR RESALE', 'PERSONAL NOT FOR RESALE'),
    ('SAMPLE', 'SAMPLE'),
    ('RETURN FOR REPAIR', 'RETURN FOR REPAIR'),
    ('RETURN AFTER REPAIR', 'RETURN AFTER REPAIR'),
]

incoterms_choices = [
    ('CIF', 'CIF'),
    ('CFR', 'CFR'),
    ('FOB', 'FOB'),
]

shipment_terms_choices = [
    ('DDU', 'DDU'),
    ('DDP', 'DDP')
]


def round_to_nearest_half(weight):
    """Rounds the given weight up to the nearest 0.0 or 0.5 increment."""
    return math.ceil(weight * 2) / 2


class AWBDetail(BaseModel):
    history = HistoricalRecords()
    is_cash_user = models.BooleanField(default=False, null=True)
    awbno = models.CharField(max_length=255, unique=True)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    hub = models.ForeignKey(
        Hub,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT
    )
    origin = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='awb_origin'
    )
    destination = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='awb_destination'
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    booking_datetime = models.DateTimeField(
        auto_now_add=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    forwarding_number = models.TextField(
        null=True,
        blank=True
    )
    forwarding_number_1 = models.TextField(
        null=True,
        blank=True
    )
    reference_number = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    shipment_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT
    )
    content = models.TextField()
    dividing_factor = models.ForeignKey(
        DividingFactor,
        related_name="awb_dividing_factor",
        on_delete=models.PROTECT,
        null=True
    )
    total_box = models.PositiveIntegerField(
        default=1
    )
    is_in_run = models.BooleanField(
        default=False
    )
    is_verified = models.BooleanField(
        default=False
    )
    is_cancelled = models.BooleanField(
        default=False,
        null=True
    )
    is_invoice_generated = models.BooleanField(
        default=False
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    total_volumetric_weight = models.FloatField(
        default=0
    )
    total_actual_weight = models.FloatField(
        default=0
    )
    total_charged_weight = models.FloatField(
        default=0
    )
    is_custom = models.BooleanField(
        default=False
    )
    barcode_image = models.ImageField(
        upload_to='barcodes/', null=True, blank=True)

    is_editable = models.BooleanField(
        default=True
    )
    is_api_called_success = models.BooleanField(
        default=False
    )
    reason_for_export = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=reason_for_export_choices
    )
    incoterms = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=incoterms_choices
    )
    shipment_terms = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=shipment_terms_choices
    )

    label_1 = models.TextField(
        null=True,
        blank=True
    )
    label_2 = models.TextField(
        null=True,
        blank=True
    )
    label_3 = models.TextField(
        null=True,
        blank=True
    )
    label_4 = models.TextField(
        null=True,
        blank=True
    )
    label_5 = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('awbno', 'is_custom')

    def save(self, *args, **kwargs):
        # Don't create awb if agency is blocked:
        if self.agency and self.agency.is_blocked:
            raise ValidationError(
                "Agency is blocked. Blocked agency can't create AWB.")
        # Only generate awbno if this is a new record and not a custom AWB
        if not self.pk and not self.is_custom:
            last_awb = AWBDetail.objects.filter(
                is_custom=False).order_by('-awbno').first()
            self.awbno = 140010011 if last_awb is None else int(
                last_awb.awbno) + 1

            while True:
                if AWBDetail.objects.filter(awbno=self.awbno).exists():
                    self.awbno = int(self.awbno) + 1
                    self.awbno = str(self.awbno)
                else:
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.awbno}"

    @property
    def total_bag(self):
        # Count only boxes with a bag_no
        return self.boxdetails.exclude(bag_no__isnull=True).count()

    @property
    def all_box_awb(self):
        # Query only once and join values
        return " | ".join(
            self.boxdetails.exclude(box_awb_no__isnull=True)
                           .values_list("box_awb_no", flat=True)
        )

    @property
    def total_box_items_amount(self):
        # Direct sum of all item amounts under this AWB
        return (
            self.boxdetails.aggregate(total=Sum("items__amount"))["total"]
            or 0
        )


@receiver(pre_save, sender='awb.AWBDetail')
def prevent_unverify_if_in_run(sender, instance, **kwargs):
    if instance.pk:  # Only for existing instances
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.is_verified and not instance.is_verified:
            # Check if AWB is in a run
            if instance.is_in_run:
                raise ValidationError(
                    "Cannot unverify an AWB that is in a run.")


@receiver(post_save, sender='awb.AWBDetail')
def update_awb_status(sender, instance, created, **kwargs):
    from django.utils import timezone
    now_date_time = timezone.now()
    if instance:
        awb_status, created = AWBStatus.objects.get_or_create(
            awb=instance,
            status='LABEL CREATED',
        )
        if created:
            awb_status.location = "KATHMANDU"
            awb_status.created_at = now_date_time
            awb_status.save()
    if instance.is_verified:
        awb_status, created = AWBStatus.objects.get_or_create(
            awb=instance,
            status='VERIFIED',
        )
        if created:
            awb_status.location = "KATHMANDU"
            awb_status.created_at = now_date_time
            awb_status.save()
    if instance.is_cancelled:
        awb_status, created = AWBStatus.objects.get_or_create(
            awb=instance,
            status='CANCELLED',
        )
        if created:
            awb_status.location = "KATHMANDU"
            awb_status.created_at = now_date_time
            awb_status.save()
    if instance.is_in_run:
        awb_status, created = AWBStatus.objects.get_or_create(
            awb=instance,
            status='ADDED TO RUN',
        )
        if created:
            awb_status.location = "KATHMANDU"
            awb_status.created_at = now_date_time
            awb_status.save()
    if instance.forwarding_number:
        awb_status, created = AWBStatus.objects.get_or_create(
            awb=instance,
            status='FORWARDING NO ASSIGNED',
        )
        if created:
            awb_status.location = "KATHMANDU"
            awb_status.created_at = now_date_time
            awb_status.save()


@receiver(pre_save, sender='awb.AWBDetail')
def generate_barcode(sender, instance, **kwargs):
    # Only generate barcode if awbno is not empty
    if not instance.awbno:
        return

    # Check if instance is being created or awbno has changed
    if instance.pk:
        old_instance = AWBDetail.objects.filter(pk=instance.pk).first()
        if old_instance and old_instance.awbno == instance.awbno:
            return  # Don't regenerate if awbno hasn't changed

    # Generate barcode
    barcode_buffer = BytesIO()
    barcode = Code128(str(instance.awbno), writer=ImageWriter())
    barcode.write(barcode_buffer)
    print(f"barcode_buffer: {barcode_buffer}")
    # Save image to model field
    file_name = f"barcode_{instance.awbno}.png"
    instance.barcode_image.save(file_name, ContentFile(
        barcode_buffer.getvalue()), save=False)


class AWBStatus(BaseModel):
    awb = models.ForeignKey(AWBDetail, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=status_choices)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Date")

    class Meta:
        unique_together = ('awb', 'status')

    def __str__(self):
        return f"{self.awb.awbno} - {self.status}"


def verify_awb_validation(awb):
    instance = awb
    errors = []

    if not instance.is_cash_user and instance.agency is None:
        errors.append("Agency is required if AWB is not cash Customer")

    if instance.company is None:
        errors.append("Company is required")

    if instance.hub is None:
        errors.append("Hub is required")

    if instance.vendor is None:
        errors.append("Vendor is required")

    if instance.origin is None:
        errors.append("Origin is required")

    if instance.destination is None:
        errors.append("Destination is required")

    if instance.product_type is None:
        errors.append("Product Type is required")

    if instance.service is None:
        errors.append("Service is required")

    if instance.shipment_value is None:
        errors.append("Shipment Value is required")

    if instance.currency is None:
        errors.append("Currency is required")

    if instance.content is None:
        errors.append("Content is required")

    if instance.consignee is None:
        errors.append("Consignee is required")

    # Consignor details
    if instance.consignor:
        if instance.consignor.company is None:
            errors.append("Consignor Company is required")
        if instance.consignor.person_name is None:
            errors.append("Consignor Person Name is required")
        if instance.consignor.address1 is None:
            errors.append("Consignor Address1 is required")
        if instance.consignor.post_zip_code is None:
            errors.append("Consignor Post Zip Code is required")
        if instance.consignor.city is None:
            errors.append("Consignor City is required")
        if instance.consignor.phone_number is None:
            errors.append("Consignor Phone Number is required")
        # if instance.consignor.email_address is None:
        #     errors.append("Consignor Email Address is required")
        # if instance.consignor.state_county is None:
        #     errors.append("Consignor State County is required")
    else:
        errors.append("Consignor is required")

    # Consignee details
    if instance.consignee:
        if instance.consignee.company is None:
            errors.append("Consignee Company is required")
        if instance.consignee.person_name is None:
            errors.append("Consignee Person Name is required")
        if instance.consignee.address1 is None:
            errors.append("Consignee Address1 is required")
        if instance.consignee.post_zip_code is None:
            errors.append("Consignee Post Zip Code is required")
        if instance.consignee.city is None:
            errors.append("Consignee City is required")
        if instance.consignee.phone_number is None:
            errors.append("Consignee Phone Number is required")
        # if instance.consignee.email_address is None:
        #     errors.append("Consignee Email Address is required")
    else:
        errors.append("Consignee is required")

    # Box details
    if instance.boxdetails.count() == 0:
        errors.append("At least one box is required")

    if errors:
        raise ValidationError(errors)


class AWBAPIResponse(BaseModel):
    awb = models.ForeignKey(
        'AWBDetail',
        on_delete=models.CASCADE,
        related_name='api_responses'
    )

    vendor = models.CharField(max_length=255)
    response = models.JSONField(null=True, blank=True)
    payload = models.JSONField(null=True, blank=True)

    request_url = models.TextField(null=True, blank=True)
    label = models.TextField(null=True, blank=True)  # stores base64 string
    pdf = models.TextField(null=True, blank=True)    # stores base64 string

    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.awb.awbno if self.awb else 'N/A'} - {self.vendor}"

    class Meta:
        verbose_name = "AWB API Response"
        verbose_name_plural = "AWB API Responses"

    @property
    def reference_no(self):
        if self.vendor == "DTDC":
            try:
                return self.response[0].get("ShipmentNumber")
            except:
                return ""
        elif self.vendor == "UBX":
            return self.response.get("AWBNo", "")
        elif self.vendor == "COURIERX":
            return self.response.get("AirwayBillNumber", "")
        # "<?xml version=\"1.0\"?>\n<FFCACourier><Shipment><Result>Success</Result><TrackingNumber>FFCAN45596</TrackingNumber><Label>PGJvZHkgc3R5bGU9Ii13ZWJraXQtcHJpbnQtY29sb3ItYWRqdXN0OiBleGFjdDsiPg0KPHRhYmxlIGZyYW1lPSJib3giIHN0eWxlPSJib3JkZXI6IDJweCBzb2xpZCBibGFjaztvdXRsaW5lOiAgc29saWQgMXB4O3ZlcnRpY2FsLWFsaWduOm1pZGRsZTtmb250LWZhbWlseTphcmlhbCxzYW5zLXNlcmlmOyAgICB3aWR0aDogMTAwJTsiPg0KICAgIDx0cj4NCiAgICAgICAgPHRkIHJvd3NwYW49IjIiPjxpbWcgc3JjPSJodHRwczovL3d3dy5maXJzdGZsaWdodGNhbmFkYS5jb20vcHVibGljL21lbXB1YmxpYy9pbWFnZXMvc19sb2dvLmpwZyIgYWx0PSJGRkNMIENPVVJJRVJTIElOQyI+PC90ZD4NCiAgICAgICAgPHRkIGFsaWduPSJjZW50ZXIiPjxpbWcgc3JjPSJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVNJQUFBQWVBUU1BQUFDeXY0R1hBQUFBQmxCTVZFWC8vLzhBQUFCVnd0TitBQUFBQVhSU1RsTUFRT2JZWmdBQUFEcEpSRUZVT0kxaitNekR6SHpnREQremdZRU5rTFJuUHZQbnYvSG5BMy80amUzUG4rYy9ZL3lINTRPOThRR0dVVldqcWtaVmphcWlpaW9BUHlEck1zWVQ2MmtBQUFBQVNVVk9SSzVDWUlJPSIgYWx0PSJiYXJjb2RlIiAgIC8+PC90ZD4NCiAgICA8L3RyPg0KICAgIDx0cj48dGQgYWxpZ249ImNlbnRlciIgc3R5bGU9InRleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTsgICAgZm9udC1zaXplOiAxMnB4OyI+KkZGQ0FONDU1OTYqPGJyPkNBTkFEQSBYPGJyPjxzdHJvbmc+PC9zdHJvbmc+PC90ZD48L3RyPg0KICAgIDx0cj48dGQgY29sc3Bhbj0iMiI+PGhyIHN0eWxlPSJtYXJnaW46IDA7Ij48L3RkPjwvdHI+DQogICAgPHRyPjx0ZCBjb2xzcGFuPSIyIiBzdHlsZT0iZm9udC1zaXplOiAxMnB4OyI+MDctMjctMjAyNTxzcGFuIHN0eWxlPSJwYWRkaW5nLWxlZnQ6NDVweDsiPjwvc3Bhbj48L3RkPjwvdHI+DQogICAgPHRyPg0KICAgICAgICA8dGQgc3R5bGU9InZlcnRpY2FsLWFsaWduOnRvcDtwYWRkaW5nLXJpZ2h0OjEwcHg7d2lkdGg6NTAlOyI+PHRhYmxlIHN0eWxlPSJ3aWR0aDoxMDAlO2xpbmUtaGVpZ2h0OiAxM3B4O2ZvbnQtc2l6ZTogMTJweDsiPg0KCQk8dGJvZHk+PHRyPjx0aCBjb2xzcGFuPSIyIiBzdHlsZT0iYmFja2dyb3VuZC1jb2xvcjogI2FhYWFhYTt0ZXh0LWFsaWduOiBsZWZ0OyI+U2hpcHBlcjwvdGg+PC90cj4NCgkJPHRyPjx0ZD5TaGlwcGVyIE5hbWUgOjwvdGQ+PHRkPlNERFNBPC90ZD48L3RyPg0KCQk8dHI+PHRkPlBob25lIDo8L3RkPjx0ZD45ODA4MjgyMjA4PC90ZD48L3RyPg0KCQk8dHI+PHRkPkNvbXBhbnkgOjwvdGQ+PHRkPlNEQURBUzwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5BZGRyZXNzIDEgOjwvdGQ+PHRkPlNEQURBUzwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5BZGRyZXNzIDIgOjwvdGQ+PHRkPjwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5DaXR5L1N0YXRlL1ppcCA6PC90ZD48dGQ+U0RBQURTL1NEQURTLzQwMzIzPC90ZD48L3RyPg0KCQk8dHI+PHRkPkNvdW50cnkgOjwvdGQ+PHRkPkNBPC90ZD48L3RyPg0KCQk8dHI+PHRkIGNvbHNwYW49IjIiPiZuYnNwOzwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5Ub3RhbCBQYWNrYWdlcyA6PC90ZD48dGQ+MTwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5Ub3RhbCBXZWlnaHQgOjwvdGQ+PHRkPjIwLjAgTGJzIC8gOS4wNyBLZzwvdGQ+PC90cj4NCgkJPHRyPjx0ZD5EaW1lbnNpb25zIDo8L3RkPjx0ZD4yMC8yMC8yMDwvdGQ+PC90cj4NCgk8L3Rib2R5PjwvdGFibGU+PC90ZD4NCiAgICAgICAgPHRkIHN0eWxlPSJ2ZXJ0aWNhbC1hbGlnbjp0b3A7cGFkZGluZy1sZWZ0OjEwcHg7d2lkdGg6NTAlOyI+DQogICAgICAgICAgICA8dGFibGUgY2xhc3M9InRhYmxlIHJlc3BvbnNpdmUgbm90ZGJnIiBzdHlsZT0id2lkdGg6MTAwJTtsaW5lLWhlaWdodDogMTNweDtmb250LXNpemU6IDEycHg7Ij4NCgkJPHRib2R5Pjx0cj48dGggY29sc3Bhbj0iMiIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNhYWFhYWE7dGV4dC1hbGlnbjogbGVmdDsiPlJlY2VpdmVyPC90aD48L3RyPg0KICAgICAgDQoJCTx0cj48dGQ+UmVjcHQgTmFtZSA6PC90ZD48dGQ+U0REU0E8L3RkPjwvdHI+DQoJCTx0cj48dGQ+UGhvbmUgOjwvdGQ+PHRkPjk4MDgyODIyMDg8L3RkPjwvdHI+DQoJCTx0cj48dGQ+Q29tcGFueSA6PC90ZD48dGQ+U0RBREFTPC90ZD48L3RyPg0KCQk8dHI+PHRkPkFkZHJlc3MgMSA6PC90ZD48dGQ+U0RBREFTPC90ZD48L3RyPg0KCQk8dHI+PHRkPkFkZHJlc3MgMiA6PC90ZD48dGQ+PC90ZD48L3RyPg0KCQk8dHI+PHRkPkNpdHkvU3RhdGUvUG9zdGFsIDo8L3RkPjx0ZD5TREFBRFMvU0RBRFMvNDAzMjM8L3RkPjwvdHI+DQoJCTx0cj48dGQ+Q291bnRyeSA6PC90ZD48dGQ+Q0E8L3RkPjwvdHI+DQogIAkJPHRyPjx0ZCBjb2xzcGFuPSIyIj4mbmJzcDs8L3RkPjwvdHI+DQoJCTx0cj48dGQ+RGVzY3JpcHRpb24gOjwvdGQ+PHRkPkJPWCBJVEVNPC90ZD48L3RyPg0KCQk8dHI+PHRkPkRlY2xhcmVkIFZhbHVlIDo8L3RkPjx0ZD5DQUQgMTIwLjAwPC90ZD48L3RyPg0KCQk8dHI+PHRkPkNoYXJnZXMgQmlsbCBUbyA6PC90ZD48dGQ+IFNISVBQRVIgPC90ZD48L3RyPg0KCQk8dHI+PHRkPlRheGVzIEJpbGwgVG8gOjwvdGQ+PHRkPjwvdGQ+PC90cj4NCgk8L3Rib2R5PjwvdGFibGU+DQogICAgICAgIDwvdGQ+DQogICAgPC90cj4NCiAgICA8dHI+PHRkIGNvbHNwYW49IjIiIGFsaWduPSJjZW50ZXIiIHN0eWxlPSJwYWRkaW5nLXRvcDogNXB4O2NvbG9yOiAjNjY2O2ZvbnQtc2l6ZTogMTJweDsiPipBbGwgY2FyZ28gaXMgc3ViamVjdGVkIHRvIGluc3BlY3Rpb24qPC90ZD48L3RyPg0KICAgIDx0cj48dGQgY29sc3Bhbj0iMiI+PGhyIHN0eWxlPSJtYXJnaW46IDAgMCAwcHg7Ij48L3RkPjwvdHI+DQogICAgPHRyPjx0ZCBjb2xzcGFuPSIyIiBhbGlnbj0iY2VudGVyIiBzdHlsZT0ibGluZS1oZWlnaHQ6IDE0cHg7Zm9udC1zaXplOiAxMnB4OyI+RkZDTCBDT1VSSUVSUyBJTkM8YnI+Mjk4MCBEUkVXIFJPQUQsIFVOSVQgMTM1PGJyPg0KQkFDSyBFTlRSQU5DRTxicj4NCk1JU1NJU1NBVUdBLE9OIEw0VCAwQTcsPGJyPg0KCQlUZWw6ICg5MDUpIDY3MyAtIDk2MzEsIEZheCA6IC0uPGJyPnd3dy5GZmNsIENvdXJpZXJzIEluYy4gPC90ZD48L3RyPg0KPC90YWJsZT4NCg0KPHRhYmxlPg0KICA8dHI+DQogICAgICA8dGQ+PHA+SS9XZSBhZ3JlZSB0aGF0IEZGQ0wgQ09VUklFUlMgSU5DIHN0YW5kYXJkIHRlcm1zIGFuZCBjb25kaXRpb25zIGFwcGx5IHRvIHRoaXMgc2hpcG1lbnQgYW5kIGxpbWl0IEZGQ0wgQ09VUklFUlMgSU5DICBsaWFiaWxpdHkgdG8gdGhlIHRlcm1zIGFuZCBjb25kaXRpb25zIGFzIGxhaWQgb3V0IG9uIHRoZSByZXZlcnNlIG9mIHRoaXMgY29weS4gV2Fyc2F3IENvbnZlbnRpb24gbWF5IGFwcGx5LiBJL1dlIHVuZGVyc3RhbmQgdGhhdCBGRkNMIENPVVJJRVJTIElOQyAgZG9lcyBub3QgY2FycnkgY2FzaC9kYW5nZXJvdXMvYmFubmVkIGdvb2RzIGFuZCB3YXJyYW50IHRoYXQgaW5mb3JtYXRpb24gY29udGFpbmVkIGluIHRoaXMgQWlyd2F5IEJpbGwgaXMgdHJ1ZSBhbmQgY29ycmVjdC4gRkZDTCBDT1VSSUVSUyBJTkPigJlzIGxpYWJpbGl0eSBzaGFsbCBub3QgZXhjZWVkIFVTJCAxMDAgZm9yIGFueSBzaGlwbWVudC4NCjwvcD48L3RkPg0KICA8L3RyPg0KICA8dHI+PHRkPiZuYnNwOzwvdGQ+PC90cj4NCiAgPHRyPg0KICAgICAgPHRkPlNoaXBwZXJzIFNpZ25hdHVyZTwvdGQ+DQogIDwvdHI+IA0KPC90YWJsZT4NCjwvYm9keT4=</Label><Invoice>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</Invoice></Shipment></FFCACourier>\n"

        elif self.vendor == "SGAU" or self.vendor == "SGCA" or self.vendor == "SGUS":
            try:
                xml_data = self.response
                # If response is bytes, decode it
                if isinstance(xml_data, bytes):
                    xml_data = xml_data.decode("utf-8")
                # If response is dict containing XML
                elif isinstance(xml_data, dict):
                    xml_data = xml_data.get("xml", "")

                tree = ET.fromstring(xml_data)
                tracking_number = tree.findtext(
                    ".//TrackingNumber")  # Finds anywhere in XML
                return tracking_number if tracking_number else ""
            except Exception as e:
                return ""
        else:
            return ""
