from django.db.models import Count, Sum, Max, F, FloatField
from django.db.models.functions import Coalesce
from awb.models import AWBDetail, BoxDetails, Consignee, Consignor
from hub.models import RunAWB, Run
from accounts.models import Agency, Company
from hub.models import Hub


def get_awb(awbno):
    awb = AWBDetail.objects.get(awbno=awbno)
    details = {
        "awb_no": str(awb.awbno).upper(),

        "awb_details": {
            "shipment_value": str(awb.shipment_value).upper() if awb.shipment_value else "",
            "currency": str(awb.currency.name).upper() if awb.currency else "",
            "origin": str(awb.origin.name).upper() if awb.origin else "",
            "origin_short_name": str(awb.origin.short_name).upper() if awb.origin else "",
            "destination": str(awb.destination.name).upper() if awb.destination else "",
            "destination_short_name": str(awb.destination.short_name).upper() if awb.destination else "",
            "booking_datetime": awb.booking_datetime,
            "total_charged_weight": str(awb.total_actual_weight).upper() if awb.total_actual_weight else "",
            "total_actual_weight": str(awb.total_actual_weight).upper() if awb.total_actual_weight else "",
            "total_volumetric_weight": str(awb.total_volumetric_weight).upper() if awb.total_volumetric_weight else "",
            "total_box_items_amount": str(awb.total_box_items_amount).upper() if awb.total_box_items_amount else "",
            "all_box_awb": str(awb.all_box_awb).upper() if awb.all_box_awb else "",
            "box_count": str(awb.total_box).upper() if awb.total_box else "",
            "service": str(awb.service.name).upper() if awb.service else "",
            "service_code": str(awb.service.code).upper() if awb.service else "",
            "vendor": str(awb.vendor).upper() if awb.vendor else "",
            "forwarding_number": str(awb.forwarding_number).upper() if awb.forwarding_number else "",
            "tracking_number": str(awb.forwarding_number).upper() if awb.forwarding_number else "",
            "reference_number": str(awb.reference_number).upper() if awb.reference_number else "",
            "content": str(awb.content).upper() if awb.content else "",
            "awb_no": str(awb.awbno).upper(),
            "is_cash_user": awb.is_cash_user,
            "product_type": str(awb.product_type.name).upper() if awb.product_type else "",
        },

        "consignee": {
            "name": str(awb.consignee.person_name or "").upper(),
            "company": str(awb.consignee.company or "").upper(),
            "address1": str(awb.consignee.address1 or "").upper(),
            "address2": str(awb.consignee.address2 or "").upper(),
            "city": str(awb.consignee.city or "").upper(),
            "state": str(awb.consignee.state_county or "").upper(),
            "country": str(awb.destination.name or "").upper(),
            "country_short_name": str(awb.destination.short_name or "").upper(),
            "state_short_name": str(awb.consignee.state_abbreviation or "").upper(),
            "postcode": str(awb.consignee.post_zip_code or "").upper(),
            "phone": str(awb.consignee.phone_number or "").upper(),
            "email": str(awb.consignee.email_address or "").upper(),
            "first_name": " ".join(awb.consignee.person_name.split(" ")[:-1]).upper() if awb.consignee.person_name else "",
            "last_name": awb.consignee.person_name.split(" ")[-1].upper() if awb.consignee.person_name else "",
        } if hasattr(awb, 'consignee') else "",

        "consignor": {
            "name": str(awb.consignor.person_name).upper(),
            "company": str(awb.consignor.company).upper(),
            "address1": str(awb.consignor.address1).upper(),
            "address2": str(awb.consignor.address2).upper(),
            "city": str(awb.consignor.city).upper(),
            "state": str(awb.consignor.state_county).upper(),
            "country": str(awb.origin.name).upper(),
            "country_short_name": str(awb.origin.short_name).upper(),
            "postcode": str(awb.consignor.post_zip_code).upper(),
            "phone": str(awb.consignor.phone_number).upper(),
            "email": str(awb.consignor.email_address).upper(),
        } if hasattr(awb, 'consignor') else "",


        "company": {
            "name": str(awb.company.name).upper(),
            "address": f"{str(awb.company.address1).upper()}, {str(awb.company.city).upper()}, {str(awb.company.country).upper()}",
            "address1": str(awb.company.address1).upper() if awb.company.address1 else "",
            "city": str(awb.company.city).upper() if awb.company.city else "",
            "state": str(awb.company.state_county).upper() if awb.company.state_county else "",
            "postcode": str(awb.company.post_zip_code).upper() if awb.company.post_zip_code else "",
            "country_short_name": str(awb.company.country.short_name).upper() if awb.company.country.short_name else "",
            "country": str(awb.company.country.name).upper() if awb.company.country.name else "",
        },
        "hub": {
            "name": str(awb.hub.name).upper() if awb.hub else "",
            "currency": str(awb.hub.currency.name).upper() if awb.hub and awb.hub.currency else "",
        } if awb.hub else "",
        "agency": {
            "name": str(awb.agency.company_name).upper() if awb.agency else "",
            "owner_name": str(awb.agency.owner_name).upper() if awb.agency and awb.agency.owner_name else "",
            "address1": str(awb.agency.address1).upper() if awb.agency and awb.agency.address1 else "",
            "zip_code": str(awb.agency.zip_code).upper() if awb.agency and awb.agency.zip_code else "",
            "address2": str(awb.agency.address2).upper() if awb.agency and awb.agency.address2 else "",
            "office_phone": str(awb.agency.contact_no_1).upper() if awb.agency and awb.agency.contact_no_1 else "",
            "email": str(awb.agency.email).upper() if awb.agency and awb.agency.email else "",
            "country": str(awb.agency.country.name).upper() if awb.agency and awb.agency.country else ""
        } if awb.agency else "",
        "boxes": [{
            "box_awb_no": box.box_awb_no,
            "actual_weight": box.actual_weight,
            "volumetric_weight": box.volumetric_weight,
            "charged_weight": box.charged_weight,
            "bag_no": box.bag_no,

            "dimensions": {
                "length": str(box.length).upper(),
                "breadth": str(box.breadth).upper(),
                "height": str(box.height).upper()
            },
            "items": [{
                "box_number": str(box.get_box_number()).upper(),
                "description": str(item.description).upper(),
                "hs_code": str(item.hs_code).upper().ljust(8, '0')[:8],
                "quantity": str(item.quantity).upper(),
                "unit_weight": str(item.unit_weight).upper(),
                "unit_type": str(item.unit_type.name).upper(),
                "unit_rate": str(item.unit_rate).upper(),
                "amount": str(item.amount).upper(),
            } for item in box.items.all()]
        } for box in awb.boxdetails.all()],

    }
    return details


class RunAWBDetailsFetcher:
    def __init__(self, run_id, include_country=None, exclude_country=None):
        self.run_id = run_id
        self.run = None
        self.include_country = include_country
        self.exclude_country = exclude_country
        self.awbs = []

    def fetch_run(self):
        try:
            self.run = Run.objects.select_related(
                'hub', 'company').get(id=self.run_id)
        except Run.DoesNotExist:
            raise ValueError(f"Run with ID {self.run_id} does not exist.")

    def fetch_awbs(self):
        qs = RunAWB.objects.filter(run=self.run)

        if self.include_country:
            qs = qs.filter(
                awb__destination__short_name__in=[
                    c.upper() for c in self.include_country
                ]
            )
        elif self.exclude_country:
            qs = qs.exclude(
                awb__destination__short_name__in=[
                    c.upper() for c in self.exclude_country
                ]
            )

        # ✅ Select all related foreign keys
        qs = qs.select_related(
            'awb__agency',
            'awb__agency__country',
            'awb__company',
            'awb__company__country',
            'awb__hub',
            'awb__hub__currency',
            'awb__currency',
            'awb__consignee',
            'awb__consignor',
            'awb__origin',
            'awb__destination',
            'awb__service',
            'awb__product_type',
        ).prefetch_related(
            'awb__boxdetails__items__unit_type'
        )

        # ✅ Annotate totals to avoid property queries
        qs = qs.annotate(
            total_actual_weight=Coalesce(
                Sum("awb__boxdetails__actual_weight"), 0.0),
            total_volumetric_weight=Coalesce(
                Sum("awb__boxdetails__volumetric_weight"), 0.0),
            total_charged_weight=Coalesce(
                Sum("awb__boxdetails__charged_weight"), 0.0),
            total_bag=Coalesce(
                Count("awb__boxdetails__bag_no", distinct=True), 0),
            total_box=Coalesce(Count("awb__boxdetails", distinct=True), 0),
            total_box_items_amount=Coalesce(
                Sum("awb__boxdetails__items__amount"), 0.0),
            highest_bag_no=Max("awb__boxdetails__bag_no"),
        )

        self.awbs = qs

    def get_details(self):
        self.fetch_run()
        self.fetch_awbs()

        results = []
        for run_awb in self.awbs:
            awb = run_awb.awb
            details = self._build_awb_details(awb)
            results.append(details)
        return results

    def _build_awb_details(self, awb):
        """Build AWB details structure in memory without additional DB queries"""
        return {
            "awb_no": str(awb.awbno or "").upper(),

            "awb_details": {
                "shipment_value": str(awb.shipment_value or "").upper(),
                "currency": str(awb.currency.name or "").upper() if awb.currency else "",
                "origin": str(awb.origin.name or "").upper() if awb.origin else "",
                "origin_short_name": str(awb.origin.short_name or "").upper() if awb.origin else "",
                "destination": str(awb.destination.name or "").upper() if awb.destination else "",
                "destination_short_name": str(awb.destination.short_name or "").upper() if awb.destination else "",
                "booking_datetime": awb.booking_datetime,
                "total_charged_weight": awb.total_actual_weight,
                "total_actual_weight": awb.total_actual_weight,
                "total_volumetric_weight": awb.total_volumetric_weight,
                "total_box_items_amount": str(getattr(awb, "total_box_items_amount", "") or "").upper(),
                "all_box_awb": str(getattr(awb, "all_box_awb", "") or "").upper(),
                "box_count": str(getattr(awb, "total_box", "") or "").upper(),
                "service": str(awb.service.name or "").upper() if awb.service else "",
                "service_code": str(awb.service.code or "").upper() if awb.service else "",
                "vendor": str(awb.vendor or "").upper(),
                "forwarding_number": str(awb.forwarding_number or "").upper(),
                "tracking_number": str(awb.forwarding_number or "").upper(),
                "reference_number": str(awb.reference_number or "").upper(),
                "content": str(awb.content or "").upper(),
                "awb_no": str(awb.awbno or "").upper(),
                "is_cash_user": awb.is_cash_user,
                "product_type": str(awb.product_type.name or "").upper() if awb.product_type else "",
            },

            "consignee": {
                "name": str(awb.consignee.person_name or "").upper(),
                "company": str(awb.consignee.company or "").upper(),
                "address1": str(awb.consignee.address1 or "").upper(),
                "address2": str(awb.consignee.address2 or "").upper(),
                "city": str(awb.consignee.city or "").upper(),
                "state": str(awb.consignee.state_county or "").upper(),
                "country": str(awb.destination.name or "").upper() if awb.destination else "",
                "country_short_name": str(awb.destination.short_name or "").upper() if awb.destination else "",
                "state_short_name": str(awb.consignee.state_abbreviation or "").upper(),
                "postcode": str(awb.consignee.post_zip_code or "").upper(),
                "phone": str(awb.consignee.phone_number or "").upper(),
                "email": str(awb.consignee.email_address or "").upper(),
                "first_name": " ".join(awb.consignee.person_name.split(" ")[:-1]).upper() if awb.consignee.person_name else "",
                "last_name": awb.consignee.person_name.split(" ")[-1].upper() if awb.consignee.person_name else "",
            } if awb.consignee else "",

            "consignor": {
                "name": str(awb.consignor.person_name or "").upper(),
                "company": str(awb.consignor.company or "").upper(),
                "address1": str(awb.consignor.address1 or "").upper(),
                "address2": str(awb.consignor.address2 or "").upper(),
                "city": str(awb.consignor.city or "").upper(),
                "state": str(awb.consignor.state_county or "").upper(),
                "country": str(awb.origin.name or "").upper() if awb.origin else "",
                "country_short_name": str(awb.origin.short_name or "").upper() if awb.origin else "",
                "postcode": str(awb.consignor.post_zip_code or "").upper(),
                "phone": str(awb.consignor.phone_number or "").upper(),
                "email": str(awb.consignor.email_address or "").upper(),
            } if awb.consignor else "",

            "company": {
                "name": str(awb.company.name or "").upper(),
                "address": f"{str(awb.company.address1 or '').upper()}, {str(awb.company.city or '').upper()}, {str(awb.company.country or '').upper()}",
                "address1": str(awb.company.address1 or "").upper(),
                "city": str(awb.company.city or "").upper(),
                "state": str(awb.company.state_county or "").upper(),
                "postcode": str(awb.company.post_zip_code or "").upper(),
                "country_short_name": str(awb.company.country.short_name or "").upper() if awb.company and awb.company.country else "",
                "country": str(awb.company.country.name or "").upper() if awb.company and awb.company.country else "",
            } if awb.company else "",

            "hub": {
                "name": str(awb.hub.name or "").upper(),
                "currency": str(awb.hub.currency.name or "").upper() if awb.hub and awb.hub.currency else "",
            } if awb.hub else "",

            "agency": {
                "name": str(awb.agency.company_name or "").upper(),
                "owner_name": str(awb.agency.owner_name or "").upper(),
                "address1": str(awb.agency.address1 or "").upper(),
                "zip_code": str(awb.agency.zip_code or "").upper(),
                "address2": str(awb.agency.address2 or "").upper(),
                "office_phone": str(awb.agency.contact_no_1 or "").upper(),
                "email": str(awb.agency.email or "").upper(),
                "country": str(awb.agency.country.name or "").upper() if awb.agency.country else ""
            } if awb.agency else "",

            "boxes": [{
                "box_awb_no": str(box.box_awb_no or ""),
                "actual_weight": str(box.actual_weight or ""),
                "volumetric_weight": str(box.volumetric_weight or ""),
                "charged_weight": str(box.charged_weight or ""),
                "bag_no": str(box.bag_no or ""),
                "dimensions": {
                    "length": str(box.length or "").upper(),
                    "breadth": str(box.breadth or "").upper(),
                    "height": str(box.height or "").upper()
                },
                "items": [{
                    "box_number": str(box.get_box_number() or "").upper(),
                    "description": str(item.description or "").upper(),
                    "hs_code": str(item.hs_code or "").ljust(8, '0')[:8],
                    "quantity": str(item.quantity or "").upper(),
                    "unit_weight": str(item.unit_weight or "").upper(),
                    "unit_type": str(item.unit_type.name or "").upper() if item.unit_type else "",
                    "unit_rate": str(item.unit_rate or "").upper(),
                    "amount": str(item.amount or "").upper(),
                } for item in box.items.all()]
            } for box in awb.boxdetails.all()],
        }
