from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models.masters import Currency
from awb.models.masters import ProductType, Service
from awb.models import AWBDetail, Consignee, Consignor, BoxDetails, BoxItem, UnitType, Company
from accounts.models import Agency, Country, DividingFactor
from hub.models import Hub
from decimal import Decimal
import random
import uuid


class Command(BaseCommand):
    help = 'Seeds the database with AWB data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed AWB data...')

        # Create Unit Types
        unit_types = [
            UnitType.objects.get_or_create(name='PCS')[0],
            UnitType.objects.get_or_create(name='KG')[0],
            UnitType.objects.get_or_create(name='BOX')[0],
        ]
        self.stdout.write('Created unit types')

        # Create required related models
        country = Country.objects.get_or_create(name='Nepal')[0]
        self.stdout.write('Created country')

        # Create agency with numeric agency_code
        agency = Agency.objects.get_or_create(
            company_name='Test Agency',
            agency_code=1001,
            owner_name='Test Owner',
            country=country,
            email='test@agency.com',
            contact_no_1='1234567890'
        )[0]
        self.stdout.write('Created agency')

        # Create currency and dividing factor
        currency = Currency.objects.get_or_create(
            name='NPR',
        )[0]
        self.stdout.write('Created currency')

        dividing_factor = DividingFactor.objects.get_or_create(
            factor=5000
        )[0]
        self.stdout.write('Created dividing factor')

        hub = Hub.objects.get_or_create(
            name='Main Hub',
            currency=currency,
            country=country
        )[0]
        company = Company.objects.get_or_create(name='Test Company')[0]
        origin = Country.objects.get_or_create(name='Kathmandu')[0]
        destination = Country.objects.get_or_create(name='Pokhara')[0]
        service = Service.objects.get_or_create(name='Express')[0]
        product_type = ProductType.objects.get_or_create(name='General')[0]
        self.stdout.write('Created other required models')

        # Helper function to generate random box data
        def generate_box_data(num_boxes, awb_no):
            boxes = []
            item_types = ['Electronics', 'Clothing', 'Books', 'Furniture', 'Food', 'Toys', 'Sports', 'Office']
            for i in range(num_boxes):
                num_items = random.randint(3, 8)  # 3-8 items per box
                items = []
                for j in range(num_items):
                    item_type = random.choice(item_types)
                    unique_id = str(uuid.uuid4())[:8]  # Generate unique identifier
                    items.append({
                        'description': f'{item_type} Item {unique_id}',
                        'hs_code': f'{random.randint(1000, 9999)}-{unique_id}',
                        'quantity': random.randint(1, 10),
                        'unit_type': random.choice(unit_types),
                        'unit_weight': round(random.uniform(0.5, 5.0), 2),
                        'unit_rate': round(random.uniform(50, 500), 2)
                    })
                boxes.append({
                    'length': random.randint(10, 50),
                    'breadth': random.randint(10, 50),
                    'height': random.randint(10, 50),
                    'actual_weight': round(random.uniform(1, 20), 2),
                    'items': items
                })
            return boxes

        # Helper function to generate random person data
        def generate_person_data(prefix):
            return {
                'person_name': f'{prefix} {random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])}',
                'company': f'{prefix} Company {random.randint(1, 100)}',
                'address1': f'{random.randint(100, 999)} {random.choice(["Main", "Oak", "Pine", "Maple", "Cedar"])} St',
                'address2': f'Suite {random.randint(100, 999)}',
                'city': random.choice(['Kathmandu', 'Pokhara', 'Lalitpur', 'Bhaktapur']),
                'state_county': 'State',
                'post_zip_code': f'{random.randint(10000, 99999)}',
                'phone_number': f'{random.randint(1000000000, 9999999999)}',
                'email_address': f'{prefix.lower()}{random.randint(1, 100)}@example.com'
            }

        # Create test AWBs
        awb_data = []
        for i in range(20):  # Generate 20 AWBs
            num_boxes = random.randint(5, 10)  # 5-10 boxes per AWB
            awb_no = f'AWBA{str(i+3).zfill(3)}'  # Start from AWB003
            awb_data.append({
                'awbno': awb_no,
                'agency': agency,
                'hub': hub,
                'company': company,
                'origin': origin,
                'destination': destination,
                'service': service,
                'product_type': product_type,
                'total_box': num_boxes,
                'is_cash_user': random.choice([True, False]),
                'is_verified': True,
                'created_at': timezone.now(),
                'shipment_value': Decimal(str(round(random.uniform(500, 5000), 2))),
                'currency': currency,
                'content': random.choice(['Electronics', 'Clothing', 'Books', 'Furniture', 'Food', 'General merchandise']),
                'dividing_factor': dividing_factor,
                'boxes': generate_box_data(num_boxes, awb_no),
                'consignee': generate_person_data('Recipient'),
                'consignor': generate_person_data('Sender')
            })

        # Create the AWBs and related data
        for awb_info in awb_data:
            try:
                # Create AWB
                awb = AWBDetail.objects.create(
                    awbno=awb_info['awbno'],
                    agency=awb_info['agency'],
                    hub=awb_info['hub'],
                    company=awb_info['company'],
                    origin=awb_info['origin'],
                    destination=awb_info['destination'],
                    service=awb_info['service'],
                    product_type=awb_info['product_type'],
                    total_box=awb_info['total_box'],
                    is_cash_user=awb_info['is_cash_user'],
                    is_verified=awb_info['is_verified'],
                    created_at=awb_info['created_at'],
                    shipment_value=awb_info['shipment_value'],
                    currency=awb_info['currency'],
                    content=awb_info['content'],
                    dividing_factor=awb_info['dividing_factor']
                )
                self.stdout.write(f'Created AWB: {awb.awbno}')
                
                # Create Consignee
                consignee = Consignee.objects.create(
                    awb=awb,
                    **awb_info['consignee']
                )
                self.stdout.write(f'Created Consignee for AWB: {awb.awbno}')
                
                # Create Consignor
                consignor = Consignor.objects.create(
                    awb=awb,
                    **awb_info['consignor']
                )
                self.stdout.write(f'Created Consignor for AWB: {awb.awbno}')
                
                # Create BoxDetails and BoxItems
                for box_info in awb_info['boxes']:
                    box = BoxDetails.objects.create(
                        awb=awb,
                        length=box_info['length'],
                        breadth=box_info['breadth'],
                        height=box_info['height'],
                        actual_weight=box_info['actual_weight']
                    )
                    self.stdout.write(f'Created Box: {box.box_awb_no} for AWB: {awb.awbno}')
                    
                    for item_info in box_info['items']:
                        BoxItem.objects.create(
                            box=box,
                            description=item_info['description'],
                            hs_code=item_info['hs_code'],
                            quantity=item_info['quantity'],
                            unit_type=item_info['unit_type'],
                            unit_weight=item_info['unit_weight'],
                            unit_rate=item_info['unit_rate'],
                            amount=Decimal(str(item_info['quantity'])) * Decimal(str(item_info['unit_rate']))
                        )
                        self.stdout.write(f'Created Item: {item_info["description"]} for Box: {box.box_awb_no}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating AWB {awb_info["awbno"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded AWB data!'))
