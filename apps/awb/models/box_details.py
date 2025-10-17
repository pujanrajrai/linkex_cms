import datetime
from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords

from .masters import UnitType, HSCODE
from .awb import AWBDetail
import math
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


def round_to_nearest_half(weight):
    """Rounds the given weight up to the nearest 0.0 or 0.5 increment."""
    return math.ceil(weight * 2) / 2


class BoxDetails(BaseModel):
    history = HistoricalRecords()
    awb = models.ForeignKey(
        AWBDetail,
        on_delete=models.PROTECT,
        related_name="boxdetails"
    )
    actual_weight = models.FloatField(help_text="Actual weight in Kg")
    length = models.FloatField(help_text="Length in cm")
    breadth = models.FloatField(help_text="Breadth in cm")
    height = models.FloatField(help_text="Height in cm")
    box_awb_no = models.CharField(max_length=100, null=True, blank=True)
    bag_no = models.PositiveBigIntegerField(null=True, blank=True)
    charged_weight = models.FloatField(
        help_text="Charged weight in Kg", null=True, blank=True)
    volumetric_weight = models.FloatField(
        help_text="Volumetric weight in Kg", null=True, blank=True)
    box_label = models.TextField(null=True, blank=True)
    box_api_response = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Box Detail"
        verbose_name_plural = "Box Details"

    def __str__(self):
        return f"{self.awb.awbno}-{self.pk}"

    def get_box_number(self):
        """Get the box number based on its position in the AWB's boxes."""
        boxes = BoxDetails.objects.filter(
            awb=self.awb, created_at__lte=self.created_at).order_by('created_at')
        for i, box in enumerate(boxes):
            if box.id == self.id:
                return i + 1
        raise ValueError("Box number not found")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


@receiver(post_save, sender=BoxDetails)
def update_total_weights(sender, instance, **kwargs):
    box_detail = instance
    awb = box_detail.awb
    total_actual_weight = sum(
        box.actual_weight for box in awb.boxdetails.all())
    total_volumetric_weight = sum(
        box.volumetric_weight for box in awb.boxdetails.all())
    total_charged_weight = sum(
        box.charged_weight for box in awb.boxdetails.all())
    awb.total_actual_weight = total_actual_weight
    awb.total_volumetric_weight = total_volumetric_weight
    awb.total_charged_weight = total_charged_weight
    awb.total_box = awb.boxdetails.count()
    awb.save()


@receiver(post_save, sender=BoxDetails)
def set_box_number(sender, instance, **kwargs):
    if not instance.box_awb_no:
        box_number = instance.get_box_number()
        instance.box_awb_no = f"{instance.awb.awbno}-{box_number}"
        instance.save()


@receiver(pre_save, sender=BoxDetails)
def set_box_awb_no_and_weights(sender, instance, **kwargs):
    # Calculate weights only if awb and dimensions are provided
    if instance.awb:
        # Use the proper attribute as defined
        dividing_factor = instance.awb.dividing_factor.factor
        instance.actual_weight = round_to_nearest_half(instance.actual_weight)
        instance.volumetric_weight = round_to_nearest_half(
            (instance.length * instance.breadth * instance.height) / dividing_factor
        )
        instance.charged_weight = max(
            instance.volumetric_weight, instance.actual_weight)


class BoxItem(BaseModel):
    history = HistoricalRecords()
    box = models.ForeignKey(
        BoxDetails, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=500)
    hs_code = models.CharField(max_length=500, null=True, blank=True)
    unit_type = models.ForeignKey(
        UnitType, on_delete=models.CASCADE, related_name="box_items")
    quantity = models.PositiveIntegerField()
    unit_weight = models.FloatField(null=True, blank=True)
    unit_rate = models.FloatField(help_text="Rate per unit")
    amount = models.FloatField(
        editable=False, help_text="Calculated as Quantity * Unit Rate")

    class Meta:
        verbose_name = "Box Item"
        verbose_name_plural = "Box Items"

    def __str__(self):
        return f"{self.box}-{self.description}"

    def save(self, *args, **kwargs):
        if self.hs_code:
            HSCODE.objects.get_or_create(
                code=self.hs_code,
                description=self.description
            )
        self.amount = float(self.quantity) * float(self.unit_rate)
        super().save(*args, **kwargs)
