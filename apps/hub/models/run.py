from hub.utils import AWBValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords
from django.db.models import Max
from django.db.models import Sum, Max, Count


class Run(BaseModel):
    history = HistoricalRecords()
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    hub = models.ForeignKey('hub.Hub', on_delete=models.CASCADE)
    run_no = models.CharField(max_length=255)
    flight_no = models.CharField(max_length=255)
    flight_departure_date = models.DateField()
    mawb_no = models.CharField(max_length=255)
    is_locked = models.BooleanField(default=False)
    manifest = models.ManyToManyField(
        'hub.ManifestFormat',
        related_name='run_manifest',
    )
    vendor = models.ForeignKey(
        'hub.Vendor',
        related_name='run_vendor',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.run_no

    @property
    def highest_bag_no(self):
        from awb.models import BoxDetails
        return (
            BoxDetails.objects
            .filter(awb__runawb__run=self)
            .aggregate(highest_bag_no=Max("bag_no"))
            ["highest_bag_no"]
        )

    @property
    def unique_bag_count(self):
        from awb.models import BoxDetails
        return (
            BoxDetails.objects
            .filter(awb__runawb__run=self)
            .values("bag_no")
            .distinct()
            .count()
        )

    @property
    def total_actual_weight(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .aggregate(total=Sum("awb__total_actual_weight"))
            ["total"] or 0
        )

    @property
    def total_volumetric_weight(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .aggregate(total=Sum("awb__total_volumetric_weight"))
            ["total"] or 0
        )

    @property
    def total_charged_weight(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .aggregate(total=Sum("awb__total_charged_weight"))
            ["total"] or 0
        )

    @property
    def total_bag(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .aggregate(total=Sum("awb__total_bag"))
            ["total"] or 0
        )

    @property
    def total_boxes(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .aggregate(total=Sum("awb__total_box"))
            ["total"] or 0
        )

    @property
    def total_shipment(self):
        return (
            RunAWB.objects
            .filter(run=self)
            .count()
        )

    @property
    def is_departed(self):
        run_status = RunStatus.objects.filter(
            run=self, status='SHIPMENT DEPARTURED').first()

        if run_status:
            return True
        return False


class RunAWB(BaseModel):
    history = HistoricalRecords()
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    awb = models.ForeignKey('awb.AWBDetail', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.awb}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Run AWB"
        verbose_name_plural = "Run AWBs"
        unique_together = ('run', 'awb')


@receiver(post_save, sender=RunAWB)
def update_awb_status_on_save(sender, instance, created, **kwargs):
    if created:  # Only when a new RunAWB is created
        # Update AWB to mark it as in a run
        awb = instance.awb
        awb.is_in_run = True
        awb.save(update_fields=['is_in_run'])


@receiver(post_delete, sender=RunAWB)
def update_awb_status_on_delete(sender, instance, **kwargs):
    # Update AWB to mark it as not in a run
    awb = instance.awb
    awb.is_in_run = False
    awb.save(update_fields=['is_in_run'])

    # Set bag_no to null for all box details related to this AWB
    from awb.models.box_details import BoxDetails
    BoxDetails.objects.filter(awb=awb).update(bag_no=None)


@receiver(pre_save, sender=RunAWB)
def can_be_added_to_run(sender, instance, **kwargs):
    AWBValidator.validate_awb_verified(instance.awb)
    AWBValidator.validate_awb_company_and_hub(instance.awb, instance.run)
    AWBValidator.validate_awb_not_in_run(instance.awb, instance.run)
    AWBValidator.is_run_locked(instance.run)


class RunStatus(BaseModel):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Date")

    class Meta:
        unique_together = ('run', 'status')

    def __str__(self):
        return self.status


@receiver(post_save, sender=RunStatus)
def update_run_awb_status(sender, instance, **kwargs):
    from awb.models.awb import AWBStatus
    run_awbs = RunAWB.objects.filter(run=instance.run)
    for run_awb in run_awbs:
        status = instance.status
        try:
            awb_status, created = AWBStatus.objects.get_or_create(
                location=instance.location,
                awb=run_awb.awb,
                status=status
            )
            if created:
                # Manually override created_at after creation
                awb_status.created_at = instance.created_at
                awb_status.save(update_fields=['created_at'])
        except Exception as e:
            print(f"Error creating AWBStatus: {e}")


@receiver(post_delete, sender=RunStatus)
def update_run_awb_status_on_delete(sender, instance, **kwargs):
    from awb.models.awb import AWBStatus
    run_awbs = RunAWB.objects.filter(run=instance.run)
    for run_awb in run_awbs:
        status = instance.status
        try:
            awb_status = AWBStatus.objects.get(awb=run_awb.awb, status=status)
            awb_status.delete()
        except Exception as e:
            print(e)
