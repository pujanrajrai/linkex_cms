from django.core.management.base import BaseCommand
from accounts.models import Country, Currency, DividingFactor, Company, User, Agency
from awb.models import DocumentType, ProductType, UnitType, Service
from hub.models import Hub, ManifestFormat, Vendor
from decimal import Decimal
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Seeding data...")
        self.seed_countries()
        self.seed_currencies()
        self.seed_dividing_factors()
        self.seed_document_types()
        self.seed_product_types()
        self.seed_unit_types()
        self.seed_services()
        self.seed_companies()
        self.seed_manifest_formats()
        self.seed_vendors()
        self.seed_hubs()
        self.seed_users()
        self.seed_agencies()
        self.stdout.write(self.style.SUCCESS("✅ Seeding complete."))

    def seed_agencies(self):

        # Assuming DividingFactor and Country are already imported
        country = Country.objects.get(name="Nepal")

        # Create and save the agency first
        agencies = [
            Agency(
                company_name="IT Nepal Solutions",
                owner_name="Pujan Raj Rai",
                country=country,
                email="itnepal@gmail.com",
                zip_code="44600",
                state="Bagmati",
                city="Kathmandu",
                address1="Lal Durbar Marg",
                contact_no_1="9808000000",
                contact_no_2="9808000000",
                credit_limit=100000,
                max_user=10,
                agency_code=109,
            )
        ]
        Agency.objects.bulk_create(agencies, ignore_conflicts=True)

    def seed_users(self):
        users = [
            User(username="admin", password=make_password("admin"),
                 email="admin@admin.com", role="admin", is_superuser=True, is_staff=True)
        ]
        User.objects.bulk_create(users, ignore_conflicts=True)

    def seed_countries(self):
        countries = [
            Country(name="Afghanistan", short_name="AF", code="+93"),
            Country(name="Albania", short_name="AL", code="+355"),
            Country(name="Algeria", short_name="DZ", code="+213"),
            Country(name="Andorra", short_name="AD", code="+376"),
            Country(name="Angola", short_name="AO", code="+244"),
            Country(name="Argentina", short_name="AR", code="+54"),
            Country(name="Armenia", short_name="AM", code="+374"),
            Country(name="Australia", short_name="AU", code="+61"),
            Country(name="Austria", short_name="AT", code="+43"),
            Country(name="Azerbaijan", short_name="AZ", code="+994"),
            Country(name="Bahamas", short_name="BS", code="+1-242"),
            Country(name="Bahrain", short_name="BH", code="+973"),
            Country(name="Bangladesh", short_name="BD", code="+880"),
            Country(name="Belarus", short_name="BY", code="+375"),
            Country(name="Belgium", short_name="BE", code="+32"),
            Country(name="Belize", short_name="BZ", code="+501"),
            Country(name="Benin", short_name="BJ", code="+229"),
            Country(name="Bhutan", short_name="BT", code="+975"),
            Country(name="Bolivia", short_name="BO", code="+591"),
            Country(name="Bosnia and Herzegovina",
                    short_name="BA", code="+387"),
            Country(name="Botswana", short_name="BW", code="+267"),
            Country(name="Brazil", short_name="BR", code="+55"),
            Country(name="Brunei", short_name="BN", code="+673"),
            Country(name="Bulgaria", short_name="BG", code="+359"),
            Country(name="Burkina Faso", short_name="BF", code="+226"),
            Country(name="Burundi", short_name="BI", code="+257"),
            Country(name="Cambodia", short_name="KH", code="+855"),
            Country(name="Cameroon", short_name="CM", code="+237"),
            Country(name="Canada", short_name="CA", code="+1"),
            Country(name="Cape Verde", short_name="CV", code="+238"),
            Country(name="Central African Republic",
                    short_name="CF", code="+236"),
            Country(name="Chad", short_name="TD", code="+235"),
            Country(name="Chile", short_name="CL", code="+56"),
            Country(name="China", short_name="CN", code="+86"),
            Country(name="Colombia", short_name="CO", code="+57"),
            Country(name="Comoros", short_name="KM", code="+269"),
            Country(name="Congo", short_name="CG", code="+242"),
            Country(name="Costa Rica", short_name="CR", code="+506"),
            Country(name="Croatia", short_name="HR", code="+385"),
            Country(name="Cuba", short_name="CU", code="+53"),
            Country(name="Cyprus", short_name="CY", code="+357"),
            Country(name="Czech Republic", short_name="CZ", code="+420"),
            Country(name="Denmark", short_name="DK", code="+45"),
            Country(name="Djibouti", short_name="DJ", code="+253"),
            Country(name="Dominican Republic", short_name="DO", code="+1-809"),
            Country(name="Ecuador", short_name="EC", code="+593"),
            Country(name="Egypt", short_name="EG", code="+20"),
            Country(name="El Salvador", short_name="SV", code="+503"),
            Country(name="Estonia", short_name="EE", code="+372"),
            Country(name="Eswatini", short_name="SZ", code="+268"),
            Country(name="Ethiopia", short_name="ET", code="+251"),
            Country(name="Fiji", short_name="FJ", code="+679"),
            Country(name="Finland", short_name="FI", code="+358"),
            Country(name="France", short_name="FR", code="+33"),
            Country(name="Gabon", short_name="GA", code="+241"),
            Country(name="Gambia", short_name="GM", code="+220"),
            Country(name="Georgia", short_name="GE", code="+995"),
            Country(name="Germany", short_name="DE", code="+49"),
            Country(name="Ghana", short_name="GH", code="+233"),
            Country(name="Greece", short_name="GR", code="+30"),
            Country(name="Guatemala", short_name="GT", code="+502"),
            Country(name="Honduras", short_name="HN", code="+504"),
            Country(name="Hong Kong", short_name="HK", code="+852"),
            Country(name="Hungary", short_name="HU", code="+36"),
            Country(name="Iceland", short_name="IS", code="+354"),
            Country(name="India", short_name="IN", code="+91"),
            Country(name="Indonesia", short_name="ID", code="+62"),
            Country(name="Iran", short_name="IR", code="+98"),
            Country(name="Iraq", short_name="IQ", code="+964"),
            Country(name="Ireland", short_name="IE", code="+353"),
            Country(name="Israel", short_name="IL", code="+972"),
            Country(name="Italy", short_name="IT", code="+39"),
            Country(name="Jamaica", short_name="JM", code="+1-876"),
            Country(name="Japan", short_name="JP", code="+81"),
            Country(name="Jordan", short_name="JO", code="+962"),
            Country(name="Kazakhstan", short_name="KZ", code="+7"),
            Country(name="Kenya", short_name="KE", code="+254"),
            Country(name="Kuwait", short_name="KW", code="+965"),
            Country(name="Kyrgyzstan", short_name="KG", code="+996"),
            Country(name="Laos", short_name="LA", code="+856"),
            Country(name="Latvia", short_name="LV", code="+371"),
            Country(name="Lebanon", short_name="LB", code="+961"),
            Country(name="Liberia", short_name="LR", code="+231"),
            Country(name="Libya", short_name="LY", code="+218"),
            Country(name="Lithuania", short_name="LT", code="+370"),
            Country(name="Luxembourg", short_name="LU", code="+352"),
            Country(name="Madagascar", short_name="MG", code="+261"),
            Country(name="Malawi", short_name="MW", code="+265"),
            Country(name="Malaysia", short_name="MY", code="+60"),
            Country(name="Maldives", short_name="MV", code="+960"),
            Country(name="Mali", short_name="ML", code="+223"),
            Country(name="Malta", short_name="MT", code="+356"),
            Country(name="Mauritania", short_name="MR", code="+222"),
            Country(name="Mauritius", short_name="MU", code="+230"),
            Country(name="Mexico", short_name="MX", code="+52"),
            Country(name="Moldova", short_name="MD", code="+373"),
            Country(name="Monaco", short_name="MC", code="+377"),
            Country(name="Mongolia", short_name="MN", code="+976"),
            Country(name="Montenegro", short_name="ME", code="+382"),
            Country(name="Morocco", short_name="MA", code="+212"),
            Country(name="Mozambique", short_name="MZ", code="+258"),
            Country(name="Myanmar", short_name="MM", code="+95"),
            Country(name="Namibia", short_name="NA", code="+264"),
            Country(name="Nepal", short_name="NP", code="+977"),
            Country(name="Netherlands", short_name="NL", code="+31"),
            Country(name="New Zealand", short_name="NZ", code="+64"),
            Country(name="Nicaragua", short_name="NI", code="+505"),
            Country(name="Niger", short_name="NE", code="+227"),
            Country(name="Nigeria", short_name="NG", code="+234"),
            Country(name="North Korea", short_name="KP", code="+850"),
            Country(name="North Macedonia", short_name="MK", code="+389"),
            Country(name="Norway", short_name="NO", code="+47"),
            Country(name="Oman", short_name="OM", code="+968"),
            Country(name="Pakistan", short_name="PK", code="+92"),
            Country(name="Palestine", short_name="PS", code="+970"),
            Country(name="Panama", short_name="PA", code="+507"),
            Country(name="Papua New Guinea", short_name="PG", code="+675"),
            Country(name="Paraguay", short_name="PY", code="+595"),
            Country(name="Peru", short_name="PE", code="+51"),
            Country(name="Philippines", short_name="PH", code="+63"),
            Country(name="Poland", short_name="PL", code="+48"),
            Country(name="Portugal", short_name="PT", code="+351"),
            Country(name="Qatar", short_name="QA", code="+974"),
            Country(name="Romania", short_name="RO", code="+40"),
            Country(name="Russia", short_name="RU", code="+7"),
            Country(name="Rwanda", short_name="RW", code="+250"),
            Country(name="Saudi Arabia", short_name="SA", code="+966"),
            Country(name="Senegal", short_name="SN", code="+221"),
            Country(name="Serbia", short_name="RS", code="+381"),
            Country(name="Singapore", short_name="SG", code="+65"),
            Country(name="Slovakia", short_name="SK", code="+421"),
            Country(name="Slovenia", short_name="SI", code="+386"),
            Country(name="South Africa", short_name="ZA", code="+27"),
            Country(name="South Korea", short_name="KR", code="+82"),
            Country(name="Spain", short_name="ES", code="+34"),
            Country(name="Sri Lanka", short_name="LK", code="+94"),
            Country(name="Sudan", short_name="SD", code="+249"),
            Country(name="Suriname", short_name="SR", code="+597"),
            Country(name="Sweden", short_name="SE", code="+46"),
            Country(name="Switzerland", short_name="CH", code="+41"),
            Country(name="Syria", short_name="SY", code="+963"),
            Country(name="Taiwan", short_name="TW", code="+886"),
            Country(name="Tajikistan", short_name="TJ", code="+992"),
            Country(name="Tanzania", short_name="TZ", code="+255"),
            Country(name="Thailand", short_name="TH", code="+66"),
            Country(name="Tunisia", short_name="TN", code="+216"),
            Country(name="Turkey", short_name="TR", code="+90"),
            Country(name="Turkmenistan", short_name="TM", code="+993"),
            Country(name="Uganda", short_name="UG", code="+256"),
            Country(name="Ukraine", short_name="UA", code="+380"),
            Country(name="United Arab Emirates", short_name="AE", code="+971"),
            Country(name="United Kingdom", short_name="GB", code="+44"),
            Country(name="USA", short_name="US", code="+1"),
            Country(name="Uruguay", short_name="UY", code="+598"),
            Country(name="Uzbekistan", short_name="UZ", code="+998"),
            Country(name="Vatican", short_name="VA", code="+379"),
            Country(name="Venezuela", short_name="VE", code="+58"),
            Country(name="Vietnam", short_name="VN", code="+84"),
            Country(name="Yemen", short_name="YE", code="+967"),
            Country(name="Zambia", short_name="ZM", code="+260"),
            Country(name="Zimbabwe", short_name="ZW", code="+263"),
        ]
        Country.objects.bulk_create(countries, ignore_conflicts=True)

    def seed_currencies(self):
        currencies = [
            Currency(name="USD", symbol="$"),
            Currency(name="EUR", symbol="€"),
            Currency(name="GBP", symbol="£"),
            Currency(name="CAD", symbol="$"),
            Currency(name="INR", symbol="₹"),
            Currency(name="NPR", symbol="₨"),
            Currency(name="AED", symbol="د.إ"),
            Currency(name="AUD", symbol="A$"),
            Currency(name="HKD", symbol="HK$"),
            Currency(name="JPY", symbol="¥"),
            Currency(name="KRW", symbol="₩"),
            Currency(name="MXN", symbol="$"),
            Currency(name="NZD", symbol="$"),
            Currency(name="PHP", symbol="₱"),
            Currency(name="SAR", symbol="﷼"),
        ]
        Currency.objects.bulk_create(currencies, ignore_conflicts=True)

    def seed_dividing_factors(self):
        dividing_factors = [
            DividingFactor(name="6000", factor=6000),
            DividingFactor(name="5500", factor=5500),
            DividingFactor(name="5000", factor=5000),
            DividingFactor(name="4500", factor=4500),
        ]
        DividingFactor.objects.bulk_create(
            dividing_factors, ignore_conflicts=True)

    def seed_document_types(self):
        document_types = [
            DocumentType(name="CITIZENSHIP"),
            DocumentType(name="PASSPORT"),
            DocumentType(name="DRIVER LICENSE"),
            DocumentType(name="NATIONAL ID"),
            DocumentType(name="VOTER ID"),
        ]
        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

    def seed_product_types(self):
        product_types = [
            ProductType(name="DOX"),
            ProductType(name="NON-DOX"),
        ]
        ProductType.objects.bulk_create(product_types, ignore_conflicts=True)

    def seed_unit_types(self):

        unit_types = [
            UnitType(name="PKT"),
            UnitType(name="PC"),
            UnitType(name="PCS"),
            UnitType(name="NOS"),
            UnitType(name="BOTTLE"),
            UnitType(name="PAIR"),
            UnitType(name="STRIP"),
            UnitType(name="SETS"),
            UnitType(name="DOZEN"),
            UnitType(name="GROSS"),
            UnitType(name="BOX"),
            UnitType(name="KG"),
            UnitType(name="GRAM"),
            UnitType(name="CONTAINER"),
            UnitType(name="CARATS"),
        ]
        UnitType.objects.bulk_create(unit_types, ignore_conflicts=True)

    def seed_services(self):
        services = [
            Service(name="SELF"),
            Service(name="DHL"),
            Service(name="FEDEX"),
            Service(name="UPS"),
            Service(name="DPD"),
            Service(name="TOLL"),
            Service(name="DTDC"),
            Service(name="GLS"),
            Service(name="TNT"),
            Service(name="DPD-DE"),
            Service(name="DPD-UK"),
            Service(name="INT"),
            Service(name="TIE"),
            Service(name="DPEX"),
        ]
        Service.objects.bulk_create(services, ignore_conflicts=True)

    def seed_companies(self):
        companies = [
            Company(name="SHIP GLOBAL NEPAL", address1="Lal Durbar Marg", post_zip_code="44600",
                    city="Kathmandu", state_county="Bagmati", country=Country.objects.get(name="Nepal"), phone_number=9808282207),
            Company(name="SHIP GLOBAL NEPAL", address1="Lal Durbar Marg", post_zip_code="44600",
                    city="Kathmandu", state_county="Bagmati", country=Country.objects.get(name="Nepal"), phone_number=9808282201),
        ]
        Company.objects.bulk_create(companies, ignore_conflicts=True)

    def seed_manifest_formats(self):
        manifest_formats = [
            ManifestFormat(name="dxb_custom",
                           display_name="DXB CUSTOM"),
            ManifestFormat(name="dxb_forwarding",
                           display_name="DXB FORWARDING"),
            ManifestFormat(name="ams", display_name="AMS"),
            ManifestFormat(name="ams_transit",
                           display_name="AMS TRANSIT"),
            ManifestFormat(name="jfk_bom_custom",
                           display_name="JFK BOM CUSTOM"),
            ManifestFormat(name="jfk_bom_forwarding",
                           display_name="JFK BOM FORWARDING"),
            ManifestFormat(name="yyz", display_name="YYZ"),
            ManifestFormat(name="jkf_axe", display_name="JFK AXE"),
            ManifestFormat(name="uk_csv_ubx_uk",
                           display_name="UK CSV UBX UK"),
            ManifestFormat(name="europe_csv",
                           display_name="EUROPE CSV"),
            ManifestFormat(name="manifiest_uxb_uk",
                           display_name="MANIFEST UXB UK"),
            ManifestFormat(name="dxb_manifiest",
                           display_name="DXB MANIFEST"),
            ManifestFormat(name="cds_manifiest_ubx_us",
                           display_name="CDS MANIFEST UBX US"),
            ManifestFormat(name="bag_details",
                           display_name="BAG DETAILS"),
            ManifestFormat(name="invoice", display_name="INVOICE"),
            ManifestFormat(name="forwarding_manifiest_aw",
                           display_name="FORWARDING MANIFEST AW"),
            ManifestFormat(name="manifiest_aw",
                           display_name="MANIFEST AW"),
            ManifestFormat(name="invoice_zip",
                           display_name="INVOICE ZIP"),
            ManifestFormat(name="smx_uk_custom_manifiest",
                           display_name="SMX UK CUSTOM MANIFEST"),
            ManifestFormat(name="smx_uk_connection_summary",
                           display_name="SMX UK CONNECTION SUMMARY"),
            ManifestFormat(name="ups_invoice_mws",
                           display_name="UPS INVOICE MWS"),
        ]
        ManifestFormat.objects.bulk_create(
            manifest_formats, ignore_conflicts=True)

    def seed_vendors(self):
        vendor_objects = [
            Vendor(name="eSHIPPER"),
            Vendor(name="Universal Delivery Solutions, LLC.(UDS)"),
            Vendor(name="American Xpress Courier (AXC)"),
            Vendor(name="Bombino Express Worldwide Inc.(BOM)"),
            Vendor(name="Safe Move Express Couriers LLC (SMX)"),
            Vendor(name="UBX UK Ltd (CUB)"),
            Vendor(name="A J Worldwide Services Limited (AJW)"),
            Vendor(name="Fast Track Express & Cargo Services"),
            Vendor(name="RoyalRahi Global Logistics Private Limited (MWX)"),
            Vendor(name="UNITED BUSINESS XPRESS LTD (UNX)"),
            Vendor(name="ECO EXPRESS LOGISTIC SOLUTION (EELS)"),
            Vendor(name="A W C CARGO LLC (TRNS DXB)"),
            Vendor(name="DPEX WORLDWIDE"),
        ]
        Vendor.objects.bulk_create(vendor_objects, ignore_conflicts=True)

    def seed_hubs(self):
        hub_objects = [
            Hub(
                name="SHIP GLOBAL NEPAL",
                hub_code="KTM",
                city="KATHMANDU",
                country=Country.objects.get(name="Nepal"),
                currency=Currency.objects.get(name="NPR")
            ),
            Hub(
                name="JFK",
                hub_code="JFK",
                city="New York",
                country=Country.objects.get(name="USA"),
                currency=Currency.objects.get(name="USD"),

            ),
            Hub(
                name="AMS",
                hub_code="AMS",
                city=None,
                country=Country.objects.get(name="Netherlands"),
                currency=Currency.objects.get(name="EUR"),
            ),
            Hub(
                name="YYZ",
                hub_code="YYZ",
                city=None,
                country=Country.objects.get(name="Canada"),
                currency=Currency.objects.get(name="CAD"),
            ),
            Hub(
                name="DELHI",
                hub_code="DEL",
                city=None,
                country=Country.objects.get(name="India"),
                currency=Currency.objects.get(name="INR")
            ),
            Hub(
                name="DXB",
                hub_code="DXB",
                city=None,
                country=Country.objects.get(name="United Arab Emirates"),
                currency=Currency.objects.get(name="AED")
            ),
            Hub(
                name="FRA",
                hub_code="FRA",
                city=None,
                country=Country.objects.get(name="Germany"),
                currency=Currency.objects.get(name="EUR")
            ),
            Hub(
                name="LHR- HV",
                hub_code="LHR",
                city=None,
                country=Country.objects.get(name="United Kingdom"),
                currency=Currency.objects.get(name="GBP")
            ),
            Hub(
                name="MEL",
                hub_code="MEL",
                city=None,
                country=Country.objects.get(name="Australia"),
                currency=Currency.objects.get(name="AUD")
            ),
            Hub(
                name="MUMBAI",
                hub_code="BOM",
                city=None,
                country=Country.objects.get(name="India"),
                currency=Currency.objects.get(name="INR")
            ),
            Hub(
                name="SIN",
                hub_code="SIN",
                city=None,
                country=Country.objects.get(name="Nepal"),
                currency=Currency.objects.get(name="NPR")
            ),
            Hub(
                name="SYD",
                hub_code="SYD",
                city=None,
                country=Country.objects.get(name="Nepal"),
                currency=Currency.objects.get(name="NPR")
            ),
            Hub(
                name="T LHR -LHR",
                hub_code="T LHR",
                city=None,
                country=Country.objects.get(name="United Kingdom"),
                currency=Currency.objects.get(name="GBP")
            ),
        ]

        Hub.objects.bulk_create(hub_objects, ignore_conflicts=True)
