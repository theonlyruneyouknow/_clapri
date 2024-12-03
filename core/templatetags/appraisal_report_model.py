from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, FloatField, \
    DecimalField, ListField, EmbeddedDocumentField, ReferenceField, BooleanField
from datetime import datetime
from decimal import Decimal

class PropertyCharacteristics(EmbeddedDocument):
    """Details about the property being appraised"""
    property_type = StringField(required=True, choices=[
        'single_family', 'multi_family', 'condo', 'townhouse',
        'commercial', 'industrial', 'land', 'mixed_use'
    ])
    year_built = IntField()
    square_footage = FloatField(required=True)
    lot_size = StringField()  # Can be in acres or square feet
    bedrooms = IntField()
    bathrooms = FloatField()  # Allow for half baths
    stories = IntField()
    basement = BooleanField(default=False)
    basement_finished = BooleanField(default=False)
    garage_type = StringField(choices=['attached', 'detached', 'none'])
    garage_capacity = IntField()
    construction_quality = StringField(choices=['low', 'fair', 'average', 'good', 'excellent'])
    condition = StringField(choices=['poor', 'fair', 'average', 'good', 'excellent'])
    exterior_material = StringField()
    roof_material = StringField()
    heating_type = StringField()
    cooling_type = StringField()

class Location(EmbeddedDocument):
    """Property location details"""
    address = StringField(required=True)
    city = StringField(required=True)
    state = StringField(required=True)
    zip_code = StringField(required=True)
    county = StringField(required=True)
    neighborhood = StringField()
    subdivision = StringField()
    zoning = StringField()
    flood_zone = StringField()
    latitude = FloatField()
    longitude = FloatField()

class Comparable(EmbeddedDocument):
    """Comparable property sale data"""
    address = StringField(required=True)
    sale_date = DateTimeField(required=True)
    sale_price = DecimalField(required=True, precision=2)
    square_footage = FloatField(required=True)
    price_per_sqft = DecimalField(precision=2)
    bedrooms = IntField()
    bathrooms = FloatField()
    year_built = IntField()
    distance_from_subject = FloatField()  # Distance in miles
    adjustments = ListField(StringField())  # List of adjustments made
    adjusted_price = DecimalField(precision=2)
    description = StringField()

class Valuation(EmbeddedDocument):
    """Valuation approaches and final value conclusion"""
    sales_comparison_value = DecimalField(precision=2)
    cost_approach_value = DecimalField(precision=2)
    income_approach_value = DecimalField(precision=2)
    final_value = DecimalField(required=True, precision=2)
    value_date = DateTimeField(required=True)
    approach_used = ListField(StringField(choices=[
        'sales_comparison', 'cost', 'income'
    ]))
    reconciliation_comments = StringField()

class AppraisalReport(Document):
    """Main appraisal report document"""
    report_number = StringField(required=True, unique=True)
    appraiser = StringField(required=True)  # Appraiser's name
    license_number = StringField(required=True)
    client_name = StringField(required=True)
    client_reference = StringField()  # Client's reference number
    intended_use = StringField(required=True)
    intended_users = ListField(StringField())
    
    # Report dates
    inspection_date = DateTimeField()
    report_date = DateTimeField(default=datetime.now)
    effective_date = DateTimeField(required=True)
    
    # Property details
    property_rights = StringField(required=True, choices=[
        'fee_simple', 'leased_fee', 'leasehold'
    ])
    location = EmbeddedDocumentField(Location, required=True)
    characteristics = EmbeddedDocumentField(PropertyCharacteristics, required=True)
    
    # Market Analysis
    market_conditions = StringField()
    marketing_time = StringField()
    exposure_time = StringField()
    highest_best_use = StringField(required=True)
    
    # Comparables and Valuation
    comparables = ListField(EmbeddedDocumentField(Comparable))
    valuation = EmbeddedDocumentField(Valuation, required=True)
    
    # Additional Information
    previous_sales = ListField(StringField())
    assumptions = ListField(StringField())
    limiting_conditions = ListField(StringField())
    scope_of_work = StringField(required=True)
    additional_comments = StringField()
    
    # Status and Tracking
    status = StringField(default='draft', choices=[
        'draft', 'review', 'completed', 'delivered', 'revised'
    ])
    revision_number = IntField(default=1)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'appraisal_reports',
        'ordering': ['-created_at'],
        'indexes': [
            'report_number',
            'client_name',
            'inspection_date',
            'report_date',
            'status'
        ]
    }

    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generate report number: YYYY-MM-####
            year = str(datetime.now().year)
            month = str(datetime.now().month).zfill(2)
            count = AppraisalReport.objects().count() + 1
            self.report_number = f"{year}-{month}-{str(count).zfill(4)}"
        
        self.updated_at = datetime.now()
        return super(AppraisalReport, self).save(*args, **kwargs)

    def get_price_per_sqft(self):
        """Calculate price per square foot"""
        if self.valuation and self.valuation.final_value and self.characteristics.square_footage:
            return round(self.valuation.final_value / self.characteristics.square_footage, 2)
        return None

    def get_comparable_summary(self):
        """Get summary statistics of comparables"""
        if not self.comparables:
            return None
            
        prices = [comp.sale_price for comp in self.comparables]
        return {
            'count': len(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'median_price': sorted(prices)[len(prices)//2]
        }

    def validate_report(self):
        """Validate report completeness"""
        required_fields = [
            'appraiser',
            'license_number',
            'client_name',
            'intended_use',
            'property_rights',
            'location',
            'characteristics',
            'highest_best_use',
            'valuation'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
                
        return {
            'is_valid': len(missing_fields) == 0,
            'missing_fields': missing_fields
        }