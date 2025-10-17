from django.core.exceptions import ValidationError
from functools import wraps


class AWBValidator:
    @staticmethod
    def validate_awb_verified(awb):
        if not awb.is_verified:
            raise ValidationError(
                f"AWB {awb} must be verified before adding to a run.")

    @staticmethod
    def validate_awb_company_and_hub(awb, run):
        if awb.company != run.company or awb.hub != run.hub or awb.vendor != run.vendor:
            raise ValidationError(
                f"AWB {awb} must belong to the same company and hub and vendor as the run.")

    @staticmethod
    def validate_awb_not_in_run(awb, current_run):
        from hub.models.run import RunAWB
        # Optimize query to only check if AWB exists in any run other than current
        existing_run_awb = RunAWB.objects.filter(
            awb=awb
        ).exclude(
            run=current_run
        ).select_related('run').first()

        if existing_run_awb:
            raise ValidationError(
                f"AWB {awb} is already in run {existing_run_awb.run.run_no}.")

    @staticmethod
    def is_run_locked(run):
        if run.is_locked:
            raise ValidationError(f"Run {run} is locked. unlock it first.")
